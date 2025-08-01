import pandas as pd
from functools import reduce


def cargar_datos_pv(ruta_archivo: str) -> pd.DataFrame:
    """Carga y preprocesa los datos de generación fotovoltaica."""
    datos = pd.read_excel(ruta_archivo)
    codigos = datos['Codigo'].drop_duplicates()

    split_data = []
    for codigo in codigos:
        d = datos[datos['Codigo'] == codigo]
        d = d.drop(['Codigo', 'Central'], axis=1)
        d = d.rename(columns={'Potencia Activa (MW)': codigo})
        split_data.append(d)

    df = reduce(
        lambda a, b: pd.merge(a, b, on='FechaHora', how='outer'), split_data
    )
    df = df.set_index('FechaHora')
    return df


def calcular_total_pv(df: pd.DataFrame) -> pd.Series:
    """Calcula la generación total fotovoltaica con las centrales del
    dataframe."""
    total = reduce(
        lambda a, b: a + b, [df[codigo] for codigo in df.columns.array]
    )
    total.name = 'Total'
    return total


def dividir_por_dia(df: pd.DataFrame) -> tuple[list[pd.DataFrame], int, int]:
    """Divide el dataframe por día y retorna una lista de dataframes junto con
    el día inicial y final."""
    dia_inicial = df.first_valid_index().day
    dia_final = df.last_valid_index().day
    dias = [df[df.index.day == dia] for dia in range(dia_inicial, dia_final)]
    return dias, dia_inicial, dia_final


def cargar_datos_edac(file_path: str) -> pd.DataFrame:
    """Carga y preprocesa los datos del EDAC."""
    EXCEL_TIMESTAMP = '1899-12-30'
    df = pd.read_excel(file_path)
    df['Time'] = pd.to_datetime(df['Time'], unit='D', origin=EXCEL_TIMESTAMP)
    df = df.set_index('Time')
    df.index = pd.to_datetime(df.index.round('2s'))
    df = df.drop(
        [
            'Pen Index',
            'Name',
            'Frecuencia Nominal (Hz)',
            'Primer Escalón del EDAC (Hz)',
            'Segundo Escalón del EDAC (Hz)',
        ],
        axis=1,
    )
    df = df.rename(
        {'Frecuencia del SENI (Hz)': 'freq', 'ERV TOTAL (MW)': 'pot'}, axis=1
    )
    return df
