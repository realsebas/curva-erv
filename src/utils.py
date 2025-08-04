from pathlib import Path
from enum import StrEnum

ESCALON_EDAC_1 = 59.3
ESCALON_EDAC_2 = 59.2
FRECUENCIA_NOMINAL = 60

RUTA_DATOS = 'datos'
RUTA_SALIDA_PV = 'out/pvgen'
RUTA_SALIDA_EDAC = 'out/edac'


class Colores(StrEnum):
    """Paleta de colores para las gráficas (o sea, la paleta de la SIE).
    Créditos a Arturo por sugerir usar la paleta en vez de colores random."""

    # Paleta primaria
    NEGRO = '#000000'
    AZUL_GRISACEO = '#3a606b'
    VERDE_AZULADO = '#5bc0be'
    GRIS_CLARO = '#a7a9ac'

    # Paleta secundaria
    NEGRO_AZULADO = '#0b132b'
    AZUL_OSCURO = '#1c2541'
    VERDE_PASTEL = '#9fedde'
    VERDE_CLARO = '#6fffe9'
    TURQUESA = '#1f7a8c'


def crear_directorios_salida(base_dir: str, intervalo: int) -> tuple[str, str]:
    """Crea los directorios de salida para el intervalo correspondiente."""
    t, unidad = (intervalo // 60, 'm') if intervalo >= 60 else (intervalo, 's')
    sufijo = f'{t}{unidad}'
    ruta_salida = f'{base_dir}/{sufijo}'
    ruta_graficas = f'{ruta_salida}/plots'
    Path(ruta_salida).mkdir(parents=True, exist_ok=True)
    Path(ruta_graficas).mkdir(parents=True, exist_ok=True)
    return ruta_salida, ruta_graficas
