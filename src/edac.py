import pandas as pd
from scipy.signal import savgol_filter


def analizar_edac(
    df_day: pd.DataFrame,
    escalon_edac: float = 59.3,
    t_busqueda: str = '2min',
    tolerancia_caida_gen: float = 0.05,
    min_incremento: float = -0.1,
    smooth_window: int = 7,
    smooth_poly: int = 2,
) -> list[dict]:
    """Analiza los eventos del EDAC en un día específico."""
    act_edac = df_day[df_day['freq'] < escalon_edac].copy()
    if act_edac.empty:
        return []

    intervalo = (df_day.index[1] - df_day.index[0]).total_seconds()
    act_edac['gap'] = act_edac.index.to_series().diff() > pd.Timedelta(
        intervalo * 1.5, 's'
    )
    act_edac['group'] = act_edac['gap'].cumsum()
    eventos = []

    for _, grp in act_edac.groupby('group'):
        t_act_edac = grp.index[0]
        t_inicio = t_act_edac - pd.Timedelta(t_busqueda)
        t_df = df_day[(df_day.index >= t_inicio) & (df_day.index <= t_act_edac)]

        curva_suave_evento = pd.Series(
            savgol_filter(
                t_df['pot'].values,
                window_length=smooth_window,
                polyorder=smooth_poly,
            ),
            index=t_df.index,
        )

        intervalo_en_horas = intervalo / 3600.0
        pendiente = curva_suave_evento.diff() / intervalo_en_horas
        posibles_inicios = pendiente[pendiente < -tolerancia_caida_gen]
        inicio_evento = (
            posibles_inicios.index[0]
            if not posibles_inicios.empty
            else t_act_edac
        )

        curva_suave_dia = pd.Series(
            savgol_filter(
                df_day['pot'].values,
                window_length=smooth_window,
                polyorder=smooth_poly,
            ),
            index=df_day.index,
        )
        pendientes_dia = curva_suave_dia.diff() / intervalo_en_horas
        pos_evento = pendientes_dia[pendientes_dia.index >= t_act_edac]
        posibles_finales = pos_evento[pos_evento > min_incremento]
        fin_evento = (
            posibles_finales.index[0]
            if not posibles_finales.empty
            else pos_evento.index[-1]
        )

        pendientes_evento = pendientes_dia[
            (pendientes_dia.index >= inicio_evento)
            & (pendientes_dia.index <= fin_evento)
        ]
        t_min = pendientes_evento.idxmin()
        p_min = pendientes_evento.min()
        f_min = df_day.loc[t_act_edac]

        eventos.append(
            {
                'inicio': inicio_evento,
                'fin': fin_evento,
                't_min': t_min,
                'p_min': p_min,
                'freq': f_min['freq'],
                't_freq': t_act_edac,
                'generacion': curva_suave_dia,
                'pendientes': pendientes_dia,
            }
        )

    return eventos
