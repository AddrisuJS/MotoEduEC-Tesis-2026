# ═══════════════════════════════════════════════════════════════════════
#  resolver_pendientes.ps1
#  Arregla los 2 casos que quedaron dudosos de mover_basura.ps1:
#    1) El PDF con tilde (problema de codificacion del script anterior,
#       aqui lo buscamos con comodin en vez de escribir la tilde)
#    2) Confirma si el .docx que dio error de "archivo en uso" en verdad
#       se movio o no, y lo reintenta si hace falta.
# ═══════════════════════════════════════════════════════════════════════

$raiz = Get-Location
$papelera = Join-Path $raiz "_basura"

Write-Host "════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host " 1) El PDF con tilde (buscando por comodin)" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════" -ForegroundColor Cyan

$pdf = Get-ChildItem -Path $raiz -Filter "Sociedad para la Conservaci*.pdf" -File -ErrorAction SilentlyContinue
if ($pdf) {
    Write-Host "Encontrado en la raiz: $($pdf.Name)" -ForegroundColor Yellow
    New-Item -ItemType Directory -Force -Path $papelera | Out-Null
    Move-Item -Path $pdf.FullName -Destination (Join-Path $papelera $pdf.Name) -Force
    Write-Host "  movido a _basura\" -ForegroundColor Green
} else {
    $enBasura = Get-ChildItem -Path $papelera -Filter "Sociedad para la Conservaci*.pdf" -File -ErrorAction SilentlyContinue
    if ($enBasura) {
        Write-Host "Ya estaba en _basura\ (nada que hacer)" -ForegroundColor Green
    } else {
        Write-Host "No lo encuentro en ningun lado. Revisa el nombre exacto con:" -ForegroundColor Red
        Write-Host "  Get-ChildItem -Filter '*.pdf'" -ForegroundColor White
    }
}

Write-Host ""
Write-Host "════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host " 2) El docx que dio 'archivo en uso'" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════" -ForegroundColor Cyan

$rel = "backend\db\SECCIONES A INCLUIR EN PLATAFORMA.docx"
$origen = Join-Path $raiz $rel
$destino = Join-Path $papelera $rel

$existeOrigen = Test-Path $origen
$existeDestino = Test-Path $destino

if ($existeDestino -and -not $existeOrigen) {
    Write-Host "Ya se habia movido correctamente. Todo bien." -ForegroundColor Green
} elseif ($existeOrigen -and -not $existeDestino) {
    Write-Host "Sigue en su lugar original. Reintentando el movimiento..." -ForegroundColor Yellow
    Write-Host "Cierra el archivo si lo tienes abierto en Word antes de continuar." -ForegroundColor Yellow
    Start-Sleep -Seconds 2
    try {
        New-Item -ItemType Directory -Force -Path (Split-Path $destino) | Out-Null
        Move-Item -Path $origen -Destination $destino -Force -ErrorAction Stop
        Write-Host "  Movido con exito ahora." -ForegroundColor Green
    } catch {
        Write-Host "  Sigue fallando: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "  Probablemente sigue abierto en algun programa. Cierralo y vuelve a correr este script." -ForegroundColor Red
    }
} elseif ($existeOrigen -and $existeDestino) {
    Write-Host "ADVERTENCIA: existe en AMBOS lados (quedo una copia a medias). Borrando la copia parcial en _basura y reintentando..." -ForegroundColor Yellow
    Remove-Item $destino -Force
    Move-Item -Path $origen -Destination $destino -Force
    Write-Host "  Resuelto." -ForegroundColor Green
} else {
    Write-Host "No existe en ninguno de los dos lados -- raro, revisa manualmente con:" -ForegroundColor Red
    Write-Host "  Get-ChildItem -Recurse -Filter '*PLATAFORMA*'" -ForegroundColor White
}
