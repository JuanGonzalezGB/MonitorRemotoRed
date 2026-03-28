param(
    [string]$Subnet = "192.168.1.0/24"
)

Write-Error "[ps1] Starting scan..."
Write-Error "[ps1] Subnet: $Subnet"

$results = @()

# Extraer base de red
$base = ($Subnet -split "/")[0]
$parts = $base -split "\."
$network = "$($parts[0]).$($parts[1]).$($parts[2])"

Write-Error "[ps1] Network base: $network"

# Limitar rango para debug (IMPORTANTE)
$range = 1..50

foreach ($i in $range) {
    $ip = "$network.$i"
    Write-Error "[ps1] Scanning $ip"

    try {
        $ping = Test-Connection -ComputerName $ip -Count 1 -Quiet -ErrorAction SilentlyContinue -TimeoutSeconds 1

        if ($ping) {
            Write-Error "[ps1] Alive: $ip"

            $latency = (Test-Connection -ComputerName $ip -Count 1).ResponseTime

            $mac = "unknown"
            $arp = arp -a | Select-String $ip

            if ($arp) {
                $mac = ($arp -split "\s+") | Where-Object {
                    $_ -match "([0-9a-f]{2}-){5}[0-9a-f]{2}"
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
        Write-Error "[ps1] Error scanning $ip"
    }
}

Write-Error "[ps1] Scan finished. Devices:" $results.Count

# OUTPUT FINAL SOLO JSON
$results | ConvertTo-Json -Compress