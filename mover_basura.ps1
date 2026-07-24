# ═══════════════════════════════════════════════════════════════════════
#  mover_basura.ps1
#  Mueve (NO borra) todo lo que no debe ir al servidor a una carpeta
#  _basura\ que conserva la misma estructura de carpetas. 100% reversible:
#  si algo se rompe, mueves los archivos de vuelta a donde estaban.
#
#  Uso:
#    cd C:\Tesis\motoeduc-tesis
#    .\mover_basura.ps1
#
#  Al final, para desplegar al servidor: copias/clonas TODO menos
#  _basura\, node_modules\, .git\, .next\, __pycache__\
# ═══════════════════════════════════════════════════════════════════════

$ErrorActionPreference = "Continue"
$raiz = Get-Location
$papelera = Join-Path $raiz "_basura"

$movidos = 0
$noEncontrados = 0

function Mover($rutaRelativa) {
    $origen = Join-Path $raiz $rutaRelativa
    if (Test-Path $origen) {
        $destino = Join-Path $papelera $rutaRelativa
        New-Item -ItemType Directory -Force -Path (Split-Path $destino) | Out-Null
        Move-Item -Path $origen -Destination $destino -Force
        Write-Host "  movido: $rutaRelativa" -ForegroundColor DarkGray
        $script:movidos++
    } else {
        Write-Host "  (no existe, se ignora): $rutaRelativa" -ForegroundColor Yellow
        $script:noEncontrados++
    }
}

Write-Host "════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host " Moviendo basura a _basura\ (nada se borra)" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════" -ForegroundColor Cyan

Write-Host "`n-- Carpetas completas (ya identificadas como obsoletas) --" -ForegroundColor Yellow
Mover "respaldo"                # copia vieja completa de backend+frontend+tests, superada
Mover ".pytest_cache"           # cache de pytest, se regenera solo

Write-Host "`n-- Raiz: scripts sueltos y docs que ya cumplieron su funcion --" -ForegroundColor Yellow
Mover "anexos_C_D_datos_2026-07-24_1356.txt"
Mover "APLICAR_MARCA.ps1"
Mover "clave_123456.sql"
Mover "datos_m4m5m6.sql"
Mover "esquema_completo.sql"
Mover "extraccion_anexos_C_D.sql"
Mover "extraccion_anexos_C_D_v2.sql"
Mover "extraccion_anexos_C_D_v2_2026-07-24_1359.txt"
Mover "extraer_anexos.ps1"
Mover "fix_detalles_15preguntas.sql"
Mover "fix_duplicados.sql"
Mover "frontend.zip"
Mover "Informe_Pasantias_MotoEduEC_2026_.docx"
Mover "INSTALACION_AUTH.md"
Mover "INSTALAR_M10.ps1"
Mover "inventario.txt"
Mover "LEEME_OPCION_A.md"
Mover "limpieza_reporte.sql"
Mover "m4m5m6.txt"
Mover "Pasos_Cambiar_Ambiente_Pasantias_Tesis.txt"
Mover "PATCH_LOGO.ps1"
Mover "PROBAR_ASISTENTE.ps1"
Mover "qa_20_participantes.sql"
Mover "qa_60_casi_real.sql"
Mover "qa_cuasi_experimental.sql"
Mover "resultados.txt"
Mover "sim_50_participantes.sql"
Mover "Sociedad para la Conservación de la Vida Silvestre__ Confirmación de pedido.pdf"
Mover "Sprint1_Documentacion_MotoEduEC_2026.docx"
Mover "Sprint2_Documentacion_MotoEduEC_2026.docx"
Mover "Sprint2_Plan_MotoEduEC_2026.docx"
Mover "Sprint3_Documentacion_MotoEduEC_2026.docx"
Mover "Sprint3_Plan_MotoEduEC_2026.docx"
Mover "Sprint4_Documentacion_MotoEduEC_2026.docx"
Mover "Sprint5_Plan_MotoEduEC_2026.docx"
Mover "tests.zip"
Mover "Wildlife Conservation Society __ Order Confirmation.pdf"

Write-Host "`n-- backend\db\ : puros scripts de migracion ya aplicados + docx que no deberian estar ahi --" -ForegroundColor Yellow
Mover "backend\db\clave_123456.sql"
Mover "backend\db\cuentas_captura.sql"
Mover "backend\db\datos_m4m5m6.sql"
Mover "backend\db\fix_detalles_simulados.sql"
Mover "backend\db\fix_garaje_encoding.sql"
Mover "backend\db\inventario.sql"
Mover "backend\db\limpiar_simulados.sql"
Mover "backend\db\limpieza_reporte.sql"
Mover "backend\db\migracion_final_ok.sql"
Mover "backend\db\migracion_usuarios_reales_v3.sql"
Mover "backend\db\migracion_usuarios_reales_v3_ok.sql"
Mover "backend\db\migration_arcade.sql"
Mover "backend\db\migration_conteo_consultas.sql"
Mover "backend\db\migration_garaje_duelos.sql"
Mover "backend\db\migration_historia_imagen.sql"
Mover "backend\db\migration_insignias.sql"
Mover "backend\db\migration_m10_grupos_revision.sql"
Mover "backend\db\migration_m11_ubicacion.sql"
Mover "backend\db\migration_m12_sesiones.sql"
Mover "backend\db\migration_m9_experimento.sql"
Mover "backend\db\migration_multi_perfil.sql"
Mover "backend\db\migration_roles.sql"
Mover "backend\db\migration_usuarios_auth.sql"
Mover "backend\db\Plataforma_MotoEduEC.docx"
Mover "backend\db\PROBAR_ASISTENTE.ps1"
Mover "backend\db\qa_60_casi_real_v2.sql"
Mover "backend\db\resultados_tesis.sql"
Mover "backend\db\schema.sql"
Mover "backend\db\SECCIONES A INCLUIR EN PLATAFORMA.docx"
Mover "backend\db\seed.sql"
Mover "backend\db\Validacion_M3_RAG.docx"

Write-Host "`n-- backend\ : backup suelto --" -ForegroundColor Yellow
Mover "backend\main.py.bak"

Write-Host "`n-- frontend\ : un .bak junto a CADA pagina (de APLICAR_MARCA.ps1) --" -ForegroundColor Yellow
Mover "frontend\app\admin\page.tsx.bak"
Mover "frontend\app\arcade\page.tsx.bak"
Mover "frontend\app\dashboard\page.tsx.bak"
Mover "frontend\app\evaluacion\page.tsx.bak"
Mover "frontend\app\gamificacion\page.tsx.bak"
Mover "frontend\app\garaje\page.tsx.bak"
Mover "frontend\app\login\page.tsx.bak"
Mover "frontend\app\page.tsx.bak"
Mover "frontend\app\registro\page.tsx.bak"
Mover "frontend\app\top\page.tsx.bak"
Mover "frontend\lib\Navbar.tsx.bak"
Mover "frontend\lib\ui.tsx.bak"
Mover "frontend\lib\ui.tsx.bak2"

Write-Host "`n-- tests\ : un duplicado con '- copia' en el nombre --" -ForegroundColor Yellow
Mover "tests\ragas_resultado_50 - copia.json"

Write-Host "`n════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host " Resumen: $movidos movidos, $noEncontrados ya no existian (ok, se ignoran)" -ForegroundColor Green
Write-Host "════════════════════════════════════════════════════" -ForegroundColor Cyan

Write-Host "`nIMPORTANTE - no mueve automatico (necesito que TU confirmes primero):" -ForegroundColor Red
Write-Host "  backend\middleware_control.py    -> revisa si main.py lo importa" -ForegroundColor Yellow
Write-Host "  seed_catalogo_tesis.py           -> probablemente redundante (el catalogo ya esta en el dump), pero confirmalo" -ForegroundColor Yellow
Write-Host "  seed_historias_reales.sql        -> idem, las historias ya estan en el dump" -ForegroundColor Yellow
Write-Host "  preguntas_ampliacion.json        -> revisa si algun script lo lee todavia" -ForegroundColor Yellow
Write-Host "  tests\ (la carpeta completa)     -> NO es basura, solo no se copia al servidor de produccion" -ForegroundColor Yellow

Write-Host "`nPara desplegar: copia/clona todo EXCEPTO _basura\, node_modules\, .git\, .next\, __pycache__\" -ForegroundColor Green
