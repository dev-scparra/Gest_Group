"""Deriva la tabla de Cayley de G a partir de una permutacion real de S5.

No se importa desde src/ en produccion (ver plan.md de 001-grupo-algebraico):
es un script auxiliar que se corre una sola vez, offline, para dejar
trazabilidad de como se obtuvo CAYLEY_G a partir de composicion de
permutaciones genuinas, en vez de inventar la tabla a mano.

Resolucion de T001-01 (spec 001, Seccion 5): se elige la Opcion A, con una
realizacion concreta que evita la contradiccion matematica de la Opcion A
literal del documento de contexto (ver docs/demostraciones.md, Decision D1):

    sigma = (1 2 3)(4 5) in S5,  orden(sigma) = lcm(3,2) = 6

G se define como el subgrupo ciclico de S5 generado por sigma:

    E  = sigma^0
    G1 = sigma^1
    G2 = sigma^2
    G3 = sigma^3   (= (4 5), el unico elemento no identidad autoinverso)
    G4 = sigma^4
    G5 = sigma^5

Esto hace a G genuinamente isomorfo a Z/6Z, subgrupo real de S5 (clausura,
asociatividad e inversos se heredan de la composicion de funciones, no se
postulan). La operacion resultante es sigma^i . sigma^j = sigma^((i+j) mod 6),
es decir G ~= Z/6Z bajo suma modular.
"""

from itertools import product

# Permutaciones representadas como tuplas de longitud 5, 0-indexadas:
# perm[i] = imagen de i (donde el "dedo" i+1 corresponde al indice i).
IDENTIDAD = (0, 1, 2, 3, 4)

# sigma = (1 2 3)(4 5) en notacion 1-indexada -> (0 1 2)(3 4) en 0-indexada:
# 0->1, 1->2, 2->0, 3->4, 4->3
SIGMA = (1, 2, 0, 4, 3)


def componer(f: tuple, g: tuple) -> tuple:
    """(f . g)(x) = f(g(x)) — composicion derecha-a-izquierda."""
    return tuple(f[g[x]] for x in range(5))


def potencia(perm: tuple, n: int) -> tuple:
    resultado = IDENTIDAD
    for _ in range(n):
        resultado = componer(perm, resultado)
    return resultado


def main() -> None:
    potencias = [potencia(SIGMA, i) for i in range(6)]

    assert len(set(potencias)) == 6, "sigma no genera 6 elementos distintos"
    assert componer(SIGMA, potencias[5]) == IDENTIDAD, "sigma^6 != identidad"

    nombres = ["Gesto.E", "Gesto.G1", "Gesto.G2", "Gesto.G3", "Gesto.G4", "Gesto.G5"]

    print("# Permutaciones generadas (verificacion):")
    for i, p in enumerate(potencias):
        print(f"#   sigma^{i} = {p}  -> {nombres[i]}")
    print()

    print("CAYLEY_G = {")
    for i, j in product(range(6), repeat=2):
        resultado = componer(potencias[i], potencias[j])
        k = potencias.index(resultado)
        print(f"    ({nombres[i]}, {nombres[j]}): {nombres[k]},")
    print("}")


if __name__ == "__main__":
    main()
