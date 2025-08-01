import pandas as pd


def suavizar_curva(
    curva: pd.Series, intervalo: int = 4, periodo: int = 3600
) -> pd.Series:
    """Suaviza la curva usando una media móvil."""
    ventana = periodo // intervalo
    return curva.rolling(ventana, center=True, min_periods=1).mean()


def suavizar_curvas(
    curvas: list[pd.DataFrame], intervalo: int, periodo: int = 3600
) -> list[pd.DataFrame]:
    """Aplica el suavizado a una lista de curvas."""
    return [
        curva.apply(lambda x: suavizar_curva(x, intervalo, periodo))
        for curva in curvas
    ]


def remuestrear_curvas(
    curvas: list[pd.DataFrame], intervalo: int
) -> list[pd.DataFrame]:
    """Remuestrea las curvas a un nuevo intervalo."""
    return [curva.resample(f'{intervalo}s').mean() for curva in curvas]
