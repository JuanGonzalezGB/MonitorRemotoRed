param(
    [string]$Subnet = "192.168.1.0/24"
)

Write-Host "[ps1] Starting scan..."
Write-Host "[ps1] Subnet: $Subnet"

$results = @()

# Extraer base de red
$base = ($Subnet -split "/")[0]
$parts = $base -split "\."
$network = "$($parts[0]).$($parts[1]).$($parts[2])"

Write-Host "[ps1] Network base: $network"

# Limitar rango para debug (IMPORTANTE)
$range = 1..50

foreach ($i in $range) {
    $ip = "$network.$i"
    Write-Host "[ps1] Scanning $ip"

    try {
        $ping = Test-Connection -ComputerName $ip -Count 1 -Quiet -ErrorAction SilentlyContinue -TimeoutSeconds 1

        if ($ping) {
            Write-Host "[ps1] Alive: $ip"

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
        Write-Host "[ps1] Error scanning $ip"
    }
}

Write-Host "[ps1] Scan finished. Devices:" $results.Count

# OUTPUT FINAL SOLO JSON
$results | ConvertTo-Json -Compress