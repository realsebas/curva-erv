import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
from src.datos import (
    cargar_datos_pv,
    dividir_por_dia,
    cargar_datos_edac,
)
from src.suavizado import suavizar_curvas, remuestrear_curvas
from src.edac import analizar_edac
from src.graficas import graficar_curvas_pv, graficar_eventos_edac
from src.utils import (
    RUTA_SALIDA_PV,
    RUTA_SALIDA_EDAC,
    ESCALON_EDAC_1,
    crear_directorios_salida,
)


def remuestrear_y_procesar(curvas, intervalo):
    remuest = remuestrear_curvas(curvas, intervalo)
    remuest_suaves = suavizar_curvas(remuest, intervalo)
    ruta_salida, ruta_graficas = crear_directorios_salida(
        RUTA_SALIDA_PV, intervalo
    )
    datos_resumen = []
    with PdfPages(f'{ruta_salida}/graficas.pdf') as pdf:
        for dia, (curva, curva_suave) in enumerate(
            zip(remuest, remuest_suaves)
        ):
            print(f'Analizando generación fotovoltaica, día {dia}')
            for central in curva.columns.array:
                datos_resumen.append(
                    graficar_curvas_pv(
                        curva_suave[central],
                        curva[central],
                        central,
                        dia,
                        ruta_graficas,
                        pdf,
                    )
                )
    resumen = pd.DataFrame(datos_resumen)
    resumen.to_csv(f'{ruta_salida}/pendientes.csv')
    resumen.to_excel(f'{ruta_salida}/pendientes.xlsx')


def procesar_datos_pv():
    """Procesa los datos de generación fotovoltaica y genera las salidas."""
    df = cargar_datos_pv('datos/Potencia Activa Centrales ERV.xlsx')
    curvas, _, _ = dividir_por_dia(df)

    # Remuestreo a 4 s (original), 1 min, 5 min y 15 min
    for intervalo in [4, 1 * 60, 5 * 60, 15 * 60]:
        remuestrear_y_procesar(curvas, intervalo)


def procesar_datos_edac():
    """Procesa los datos del EDAC data y genera las salidas."""
    df = cargar_datos_edac('datos/edac_data.xlsx')
    grupos = df.groupby(df.index.date)
    eventos = []

    # Los datos del EDAC tienen 2 s de resolución
    out_dir, plots_dir = crear_directorios_salida(RUTA_SALIDA_EDAC, 2)

    with PdfPages(f'{out_dir}/graficas.pdf') as pdf:
        for dia, df_dia in grupos:
            print(f'Analizando eventos del EDAC, día {dia}')
            eventos_dia = analizar_edac(df_dia)
            if not eventos_dia:
                print(
                    f'No se encontraron eventos de actuación del EDAC para el día {dia}.'
                )
                continue
            for evento in eventos_dia:
                dur = (evento['inicio'] - evento['fin']).total_seconds()
                eventos.append(
                    {
                        'Inicio evento': evento['fin'],
                        'Fin evento': evento['inicio'],
                        'Duracion evento (s)': dur,
                        'Pendiente mínima (MW/s)': evento['p_min'] / 3600,
                        'Hora pendiente mínima': evento['t_min'],
                        'Frecuencia (Hz)': evento['freq'],
                        'Hora frecuencia': evento['t_freq'],
                    }
                )
            graficar_eventos_edac(
                df_dia,
                eventos_dia,
                escalon_edac=ESCALON_EDAC_1,
                escalado_extra_pot=0.15,
                ruta_archivo=f'{plots_dir}/{dia}',
                pdf=pdf,
            )
    e_df = pd.DataFrame(eventos)
    e_df.to_excel(f'{out_dir}/eventos.xlsx')


if __name__ == '__main__':
    procesar_datos_pv()
    procesar_datos_edac()
