"""CLI: imprime ker(phi), Im(phi), clases laterales y verificacion de phi.

Ejecutar con: python -m src.algebra.analisis

No requiere camara ni argumentos (US-5, HOM-FR-009). La salida de este script
es el artefacto que se anexa como evidencia en docs/demostraciones.md para
las Demostraciones 2 y 3 del documento de contexto.
"""

from src.algebra.grupo_gestos import Gesto
from src.algebra.homomorfismo import Homomorfismo


def _formatear_clases(clases: dict) -> str:
    lineas = []
    for accion, gestos in sorted(clases.items(), key=lambda kv: kv[0].name):
        etiquetas = ", ".join(g.name for g in gestos)
        lineas.append(f"    ker(phi)*g para phi(g)={accion.name}: {{{etiquetas}}}")
    return "\n".join(lineas)


def generar_reporte() -> str:
    phi = Homomorfismo()

    kernel = phi.kernel()
    imagen = phi.imagen()
    clases = phi.clases_laterales_kernel()
    reporte_hom = phi.verificar_homomorfismo()

    inyectiva = phi.es_inyectiva()
    sobreyectiva = phi.es_sobreyectiva()
    if inyectiva and sobreyectiva:
        tipo = "isomorfismo (inyectiva + sobreyectiva)"
    elif inyectiva:
        tipo = "monomorfismo (inyectiva, no sobreyectiva)"
    elif sobreyectiva:
        tipo = "epimorfismo (sobreyectiva, no inyectiva)"
    else:
        tipo = "ni inyectiva ni sobreyectiva"

    lineas = [
        "=" * 60,
        "GestGroup — Analisis algebraico de phi : G -> A",
        "=" * 60,
        "",
        f"G = {{{', '.join(g.name for g in Gesto)}}}   (|G| = {len(list(Gesto))})",
        f"tabla phi por defecto: {{{', '.join(f'{g.name}->{a.name}' for g, a in phi.tabla_phi.items())}}}",
        "",
        f"ker(phi) = {{{', '.join(g.name for g in kernel)}}}   (|ker(phi)| = {len(kernel)})",
        f"Im(phi)  = {{{', '.join(a.name for a in imagen)}}}   (|Im(phi)| = {len(imagen)})",
        "",
        f"es_inyectiva()   = {inyectiva}",
        f"es_sobreyectiva()= {sobreyectiva}",
        f"tipo de phi      = {tipo}",
        "",
        "Clases laterales de ker(phi) en G (= G/ker(phi)):",
        _formatear_clases(clases),
        f"  numero de clases = {len(clases)}, |Im(phi)| = {len(imagen)}"
        f"  -> {'coinciden (Primer Teorema de Isomorfismo verificado)' if len(clases) == len(imagen) else 'NO coinciden (revisar tabla phi)'}",
        "",
        "Verificacion de la propiedad de homomorfismo phi(g1 o g2) = phi(g1) o phi(g2):",
        f"  pares evaluados = 36 (|G| x |G|)",
        f"  cumple = {reporte_hom.cumple}",
    ]
    if not reporte_hom.cumple:
        lineas.append(f"  pares fallidos = {reporte_hom.pares_fallidos}")
    lineas.append("=" * 60)
    return "\n".join(lineas)


if __name__ == "__main__":
    print(generar_reporte())
