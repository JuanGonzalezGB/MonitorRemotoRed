param(
    [string]$Subnet = "192.168.1.0/24"
)

# Función para log (stderr sin romper ejecución)
function Log {
    param($msg)
    [Console]::Error.WriteLine($msg)
}

Log "[ps1] Starting scan..."
Log "[ps1] Subnet: $Subnet"

$results = @()

# Extraer base de red
$base = ($Subnet -split "/")[0]
$parts = $base -split "\."
$network = "$($parts[0]).$($parts[1]).$($parts[2])"

Log "[ps1] Network base: $network"

# Rango limitado (debug)
$range = 1..50

foreach ($i in $range) {
    $ip = "$network.$i"
    Log "[ps1] Scanning $ip"

    try {
        $ping = Test-Connection -ComputerName $ip -Count 1 -Quiet -ErrorAction SilentlyContinue -TimeoutSeconds 1

        if ($ping -eq $true) {
            Log "[ps1] Alive: $ip"

            $latency = (Test-Connection -ComputerName $ip -Count 1 -ErrorAction SilentlyContinue).ResponseTime

            $mac = "unknown"
            $arp = arp -a | Select-String $ip

            if ($arp) {
                $mac_match = ($arp -split "\s+") | Where-Object {
                    $_ -match "([0-9a-f]{2}-){5}[0-9a-f]{2}"
                }
                if ($mac_match) {
                    $mac = $mac_match
                }
            }

            $results += @{
                ip = $ip
                mac = $mac
                vendor = "unknown"
                ping_ms = $latency
            }
        }
    }
    catch {
        Log "[ps1] FAIL $ip"
    }
}

Log "[ps1] Scan finished. Devices: $($results.Count)"

# 🔥 SOLO JSON en stdout
$results | ConvertTo-Json -Compress