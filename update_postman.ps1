$envContent = Get-Content ".env"
$apiKey = ($envContent | Where-Object { $_ -match "^POSTMAN_API_KEY=" }) -replace "POSTMAN_API_KEY=", ""
$collectionUid = ($envContent | Where-Object { $_ -match "^POSTMAN_COLLECTION_UID=" }) -replace "POSTMAN_COLLECTION_UID=", ""

Write-Host "Generando schema..."
docker compose exec api python manage.py spectacular --file schema.yml
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: fallo al generar el schema. Revisa que el contenedor este corriendo."
    exit 1
}

Write-Host "Convirtiendo a collection..."
openapi2postmanv2 -s schema.yml -o collection.json -p
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: fallo la conversion a collection."
    exit 1
}

$collectionData = Get-Content "collection.json" -Raw -Encoding UTF8 | ConvertFrom-Json
$jsonString = @{ collection = $collectionData } | ConvertTo-Json -Depth 100
$bodyBytes = [System.Text.Encoding]::UTF8.GetBytes($jsonString)

try {
    if ([string]::IsNullOrWhiteSpace($collectionUid)) {
        Write-Host "No hay COLLECTION_UID, creando collection nuevo..."
        $response = Invoke-RestMethod -Uri "https://api.getpostman.com/collections" `
            -Method Post `
            -Headers @{ "X-Api-Key" = $apiKey } `
            -ContentType "application/json; charset=utf-8" `
            -Body $bodyBytes
    } else {
        Write-Host "Actualizando collection existente..."
        $response = Invoke-RestMethod -Uri "https://api.getpostman.com/collections/$collectionUid" `
            -Method Put `
            -Headers @{ "X-Api-Key" = $apiKey } `
            -ContentType "application/json; charset=utf-8" `
            -Body $bodyBytes
    }
    $response | ConvertTo-Json -Depth 10
} catch {
    Write-Host "ERROR en la llamada a la API de Postman:"
    Write-Host $_.Exception.Message
    if ($_.ErrorDetails) { Write-Host $_.ErrorDetails.Message }
}

Write-Host "Listo."