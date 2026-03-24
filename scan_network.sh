#!/bin/bash
# scan_network.sh — escanea la red y devuelve JSON
# Uso: bash scan_network.sh [subnet]

SUBNET="${1:-192.168.1.0/24}"

# Auto-detectar path de arp-scan
ARP_SCAN=$(which arp-scan 2>/dev/null)
if [[ -z "$ARP_SCAN" ]]; then
    for P in /usr/sbin/arp-scan /usr/bin/arp-scan /sbin/arp-scan; do
        [[ -x "$P" ]] && ARP_SCAN="$P" && break
    done
fi

if [[ -z "$ARP_SCAN" ]]; then
    echo '{"error":"arp-scan no encontrado. Instalar con: sudo apt install arp-scan"}' >&2
    echo "[]"
    exit 1
fi

# Detectar interfaz activa (excluye lo/loopback)
IFACE=$(ip route | grep default | awk '{print $5}' | head -1)
if [[ -z "$IFACE" ]]; then
    IFACE=$(ip link show | grep -v loopback | grep "state UP" | awk -F': ' '{print $2}' | head -1)
fi

RESULTS=()

while IFS=$'\t' read -r ip mac vendor; do
    [[ "$ip" =~ ^[0-9]{1,3}\.[0-9]{1,3} ]] || continue

    PING_OUT=$(ping -c 1 -W 1 "$ip" 2>/dev/null)
    PING=$(echo "$PING_OUT" | grep -oP 'time=\K[\d.]+' | head -1)
    PING_VAL=${PING:-null}

    VENDOR_SAFE=$(echo "$vendor" | sed 's/"/\\"/g; s/\\/\\\\/g')
    RESULTS+=("{\"ip\":\"$ip\",\"mac\":\"$mac\",\"vendor\":\"$VENDOR_SAFE\",\"ping_ms\":$PING_VAL}")
done < <(sudo "$ARP_SCAN" ${IFACE:+--interface="$IFACE"} "$SUBNET" 2>/dev/null | grep -E "^[0-9]" | sort -u -k1,1)

if [ ${#RESULTS[@]} -eq 0 ]; then
    echo "[]"
else
    OUTPUT="["
    for i in "${!RESULTS[@]}"; do
        OUTPUT+="${RESULTS[$i]}"
        [[ $i -lt $((${#RESULTS[@]}-1)) ]] && OUTPUT+=","
    done
    OUTPUT+="]"
    echo "$OUTPUT"
fi
