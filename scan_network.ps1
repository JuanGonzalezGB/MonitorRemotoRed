param(
    [string]$Subnet = "192.168.1.0/24"
)

$results = @()

# Obtener IP base (ej: 192.168.1)
$base = ($Subnet -split "/")[0]
$parts = $base -split "\."
$network = "$($parts[0]).$($parts[1]).$($parts[2])"

# Escanear rango 1-254
1..254 | ForEach-Object {
    $ip = "$network.$_"

    # Ping rápido
    $ping = Test-Connection -ComputerName $ip -Count 1 -Quiet -ErrorAction SilentlyContinue

    if ($ping) {
        # Obtener MAC desde ARP
        $arp = arp -a | Select-String $ip
        $mac = "unknown"

        if ($arp) {
            $line = ($arp -split "\s+") | Where-Object { $_ -match "([0-9a-f]{2}-){5}[0-9a-f]{2}" }
            if ($line) {
                $mac = $line
            }
        }

        # Obtener latencia
        $latency = (Test-Connection -ComputerName $ip -Count 1).ResponseTime

        $results += [PSCustomObject]@{
            ip       = $ip
            mac      = $mac
            vendor   = "unknown"
            ping_ms  = $latency
        }
    }
}

# Salida JSON
$results | ConvertTo-Json -Compress