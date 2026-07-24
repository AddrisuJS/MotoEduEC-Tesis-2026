"""
VERIFICADOR DE IDENTIDAD DEL EMBEDDING — MotoEdu EC
====================================================
Este script existe por una razon concreta.

En este proyecto, el indexador (seed_tesis.py) y el consultante
(backend/routers/asistente.py) usaban la funcion hash() nativa de Python para
construir los vectores. Desde Python 3.3, hash() sobre cadenas esta
aleatorizado por proceso: cada proceso arranca con una semilla distinta. El
resultado fue que los vectores del indice y los de las consultas pertenecian a
espacios diferentes, y la recuperacion funcionaba por azar.

El sistema NUNCA lanzo un error. No hubo excepcion, ni log, ni alerta. El
comentario del codigo incluso afirmaba "Embedding deterministico por hash",
que era exactamente lo contrario de la verdad. Solo una metrica objetiva
(faithfulness = 0.351) lo delato.

Este verificador convierte esa leccion en un control automatico: compara el
bloque canonico de embedding de ambos archivos y falla si difieren en un solo
byte.

Uso:
    python tests/verificar_embedding.py

Ejecutarlo SIEMPRE antes de reindexar (python seed_tesis.py) y despues de
cualquier cambio en la funcion de embedding.

Codigo de salida: 0 si son identicos, 1 si divergen.
"""
import hashlib
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ARCHIVOS = {
    "seed_tesis.py":                RAIZ / "seed_tesis.py",
    "backend/routers/asistente.py": RAIZ / "backend" / "routers" / "asistente.py",
}

INICIO = "# ════════════════════════════════════════════════════════════════════════\n# BLOQUE CANONICO DE EMBEDDING"
FIN = "# ════════════════════ FIN DEL BLOQUE CANONICO ═══════════════════════════"


def extraer_bloque(ruta: Path) -> str:
    texto = ruta.read_text(encoding="utf-8")
    i = texto.find("BLOQUE CANONICO DE EMBEDDING")
    if i < 0:
        return ""
    # Retroceder al inicio de la linea de cabecera
    i = texto.rfind("# ═", 0, i)
    j = texto.find(FIN, i)
    if j < 0:
        return ""
    return texto[i:j + len(FIN)]


def version_declarada(bloque: str) -> str:
    m = re.search(r'EMBED_VERSION\s*=\s*"([^"]+)"', bloque)
    return m.group(1) if m else "?"


def main() -> int:
    print("=" * 68)
    print("  VERIFICACION DE IDENTIDAD DEL EMBEDDING")
    print("=" * 68)
    print()

    bloques = {}
    for nombre, ruta in ARCHIVOS.items():
        if not ruta.exists():
            print(f"  ❌ No existe: {ruta}")
            return 1
        b = extraer_bloque(ruta)
        if not b:
            print(f"  ❌ {nombre}: no se encontro el bloque canonico.")
            print(f"     ¿Se edito el embedding sin los marcadores de bloque?")
            return 1
        bloques[nombre] = b
        h = hashlib.sha256(b.encode()).hexdigest()
        print(f"  {nombre}")
        print(f"     version: {version_declarada(b)}")
        print(f"     sha256:  {h[:48]}")
        print(f"     bytes:   {len(b)}")
        print()

    hashes = {hashlib.sha256(b.encode()).hexdigest() for b in bloques.values()}

    print("=" * 68)
    if len(hashes) == 1:
        print("  ✅ IDENTICOS")
        print()
        print("  El indexador y el consultante comparten exactamente la misma")
        print("  funcion de embedding. El indice y las consultas viven en el")
        print("  mismo espacio vectorial.")
        print("=" * 68)
        return 0

    print("  🚨 DIVERGEN — NO REINDEXAR")
    print()
    print("  Los bloques de embedding NO son identicos. Si se indexa asi, la")
    print("  recuperacion fallara EN SILENCIO: sin errores, sin logs, solo")
    print("  documentos irrelevantes y metricas que caen sin explicacion.")
    print()
    print("  Es exactamente el fallo que ya ocurrio en este proyecto.")
    print()
    print("  Accion: copiar el bloque de un archivo al otro, byte por byte,")
    print("  desde la cabecera hasta la linea 'FIN DEL BLOQUE CANONICO'.")
    print()

    # Mostrar la primera linea que difiere
    nombres = list(bloques)
    a = bloques[nombres[0]].splitlines()
    b = bloques[nombres[1]].splitlines()
    for n, (la, lb) in enumerate(zip(a, b), 1):
        if la != lb:
            print(f"  Primera diferencia, linea {n} del bloque:")
            print(f"    {nombres[0]}: {la.strip()[:60]}")
            print(f"    {nombres[1]}: {lb.strip()[:60]}")
            break
    else:
        if len(a) != len(b):
            print(f"  Distinta cantidad de lineas: {len(a)} vs {len(b)}")
    print("=" * 68)
    return 1


if __name__ == "__main__":
    sys.exit(main())
