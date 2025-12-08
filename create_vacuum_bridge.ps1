# Create a Matter Bridge for Vacuum Entities
# This script creates a second Matter bridge instance that only includes vacuum domain entities

$apiUrl = "/api/matter/bridges"

# Bridge configuration
$bridgeConfig = @{
    name = "Vacuum Bridge"
    port = 5541  # Different port from default bridge (5540)
    filter = @{
        include = @(
            @{
                type = "domain"
                value = "vacuum"
            }
        )
        exclude = @()
    }
} | ConvertTo-Json -Depth 10

Write-Host "Creating Matter bridge for vacuum entities..." -ForegroundColor Cyan
Write-Host "API URL: $apiUrl" -ForegroundColor Gray
Write-Host "Configuration:" -ForegroundColor Gray
Write-Host $bridgeConfig -ForegroundColor Gray
Write-Host ""

try {
    $response = Invoke-RestMethod -Uri $apiUrl -Method POST -ContentType "application/json" -Body $bridgeConfig
    
    Write-Host "✅ Bridge created successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Bridge Details:" -ForegroundColor Cyan
    Write-Host "  ID: $($response.id)" -ForegroundColor White
    Write-Host "  Name: $($response.name)" -ForegroundColor White
    Write-Host "  Port: $($response.port)" -ForegroundColor White
    Write-Host "  Status: $($response.status)" -ForegroundColor White
    Write-Host ""
    
    if ($response.commissioning) {
        Write-Host "Commissioning Info:" -ForegroundColor Cyan
        Write-Host "  QR Code: $($response.commissioning.qrPairingCode)" -ForegroundColor Yellow
        Write-Host "  Manual Code: $($response.commissioning.manualPairingCode)" -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "You can now pair this bridge with your Matter controller using the codes above." -ForegroundColor Green
    
    return $response
    
} catch {
    Write-Host "❌ Error creating bridge:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    
    if ($_.Exception.Response) {
        $reader = [System.IO.StreamReader]::new($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "Response: $responseBody" -ForegroundColor Red
    }
}
