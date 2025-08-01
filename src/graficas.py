import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_pdf import PdfPages
from src.utils import Colores, FRECUENCIA_NOMINAL


def graficar_curvas_pv(
    curva: pd.Series,
    curva_orig: pd.Series,
    central: str,
    dia: int,
    ruta_salida: str,
    pdf: PdfPages,
) -> dict:
    """Grafica las curvas de generación fotovoltaica y calcula las pendientes
    máxima y mínima."""
    p_max_ini, p_max_fin = 6, 11
    p_min_ini, p_min_fin = 14, 19
    horas = curva.index.hour
    p_max_range = (horas >= p_max_ini) & (horas < p_max_fin)
    p_min_range = (horas >= p_min_ini) & (horas < p_min_fin)

    dt = (curva.index[1] - curva.index[0]).total_seconds()
    pendientes = pd.Series(np.gradient(curva, dt), curva.index)
    pendientes_pmax = pendientes.copy()
    pendientes_pmax[~p_max_range] = np.nan
    max_idx = np.nanargmax(pendientes_pmax)
    max_h = curva.index[max_idx]
    max_pendiente = pendientes.iloc[max_idx]

    pendientes_pmin = pendientes.copy()
    pendientes_pmin[~p_min_range] = np.nan
    min_idx = np.nanargmin(pendientes_pmin)
    min_h = curva.index[min_idx]
    min_pendiente = pendientes.iloc[min_idx]

    max_h_inicio = max_h.floor('h')
    max_h_fin = max_h_inicio + pd.Timedelta(hours=1)
    min_h_inicio = min_h.floor('h')
    min_h_fin = min_h_inicio + pd.Timedelta(hours=1)

    cond_max = (curva.index >= max_h_inicio) & (curva.index <= max_h_fin)
    cond_min = (curva.index >= min_h_inicio) & (curva.index <= min_h_fin)

    # Posición de las anotaciones para que no cubran la curva ni se solapen
    # entre ellas
    dur = (curva.index[-1] - curva.index[0]).total_seconds()
    rel_pos_max = (curva.index[max_idx] - curva.index[0]).total_seconds() / dur
    rel_pos_min = (curva.index[min_idx] - curva.index[0]).total_seconds() / dur
    off_x_max = -1 if rel_pos_max < 0.5 else 1
    off_x_min = -1 if rel_pos_min < 0.5 else 1
    off_y_max = -1 if curva.iloc[max_idx] < curva.mean() else 1
    off_y_min = -1 if curva.iloc[min_idx] < curva.mean() else 1

    time_diff_sec = abs(
        (curva.index[max_idx] - curva.index[min_idx]).total_seconds()
    )

    if time_diff_sec < 2 * 3600:
        off_x_max *= 0.5
        off_x_min *= 1.5
        off_y_max *= 1.5
        off_y_min *= -1.5

    off_x_max *= 80
    off_x_min *= 80
    off_y_max *= 20
    off_y_min *= 20

    plt.figure(figsize=(12, 6))

    plt.plot(
        curva.index,
        curva_orig,
        label='Original',
        color=Colores.VERDE_CLARO,
        alpha=0.4,
    )
    plt.plot(
        curva.index,
        curva,
        label='Suave',
        color=Colores.AZUL_GRISACEO,
        linewidth=2,
    )
    plt.fill_between(
        curva.index[cond_max],
        0,
        curva[cond_max],
        color=Colores.GRIS_CLARO,
        alpha=0.25,
        label='Periodo de máxima pendiente',
    )
    plt.fill_between(
        curva.index[cond_min],
        0,
        curva[cond_min],
        color=Colores.GRIS_CLARO,
        alpha=0.25,
        label='Periodo de mínima pendiente',
    )
    plt.scatter(
        curva.index[max_idx],
        curva.iloc[max_idx],
        color=Colores.AZUL_GRISACEO,
        s=80,
        marker='o',
    )
    plt.scatter(
        curva.index[min_idx],
        curva.iloc[min_idx],
        color=Colores.AZUL_GRISACEO,
        s=80,
        marker='o',
    )

    plt.annotate(
        'Máxima pendiente\n'
        f'{max_pendiente * 3600:.1f} MW/h\n'
        f'{curva.index[max_idx].strftime("%H:%M")}',
        (curva.index[max_idx], curva.iloc[max_idx]),
        (off_x_max, off_y_max),
        textcoords='offset points',
        arrowprops={'arrowstyle': '-'},
        color=Colores.NEGRO,
        fontsize=9,
        ha='center',
        va='center',
    )
    plt.annotate(
        'Mínima pendiente\n'
        f'{min_pendiente * 3600:.1f} MW/h\n'
        f'{curva.index[min_idx].strftime("%H:%M")}',
        (curva.index[min_idx], curva.iloc[min_idx]),
        (off_x_min, off_y_min),
        textcoords='offset points',
        arrowprops={'arrowstyle': '-'},
        color=Colores.NEGRO,
        fontsize=9,
        ha='center',
        va='center',
    )

    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H'))
    plt.xticks(rotation=0)
    xlim1 = curva.index[0].normalize()
    xlim2 = xlim1 + pd.Timedelta(days=1)
    plt.xlim(xlim1, xlim2)
    plt.ylim(0)
    plt.xlabel('Hora')
    plt.ylabel('Potencia activa (MW)')
    plt.title(f'{central}, día {curva.index.day[0]}')
    plt.legend()
    plt.grid()
    plt.tight_layout()

    titulo = f'{central}-d{curva.index.day[0]}'
    plt.savefig(f'{ruta_salida}/{titulo}.png')
    pdf.savefig()
    plt.close()

    return {
        'Día': curva.index[0].date(),
        'Central': central,
        'Máxima pendiente (MW/h)': max_pendiente * 3600,
        'H max': curva.index[max_idx].strftime('%H:%M'),
        'P max': max_h_fin.strftime('P%H'),
        'Mínima pendiente (MW/h)': min_pendiente * 3600,
        'H min': curva.index[min_idx].strftime('%H:%M'),
        'P min': min_h_fin.strftime('P%H'),
    }


def graficar_eventos_edac(
    df_day: pd.DataFrame,
    eventos: list[dict],
    *,
    escalon_edac: float,
    escalado_extra_pot: float,
    ruta_archivo: str,
    pdf: PdfPages,
):
    """Grafica los eventos del EDAC."""
    fig, ax_pot = plt.subplots(figsize=(12, 6))
    ax_pot.plot(
        eventos[0]['generacion'].index,
        eventos[0]['generacion'],
        color=Colores.AZUL_GRISACEO,
        label='ERV total',
    )

    # Ajusta la escala de generación para facilitar la visualización
    ymin, ymax = ax_pot.get_ylim()
    y_range = ymax - ymin
    margin = escalado_extra_pot
    ax_pot.set_ylim(ymin - y_range * margin, ymax + y_range * margin)
    ax_pot.set_xlim(df_day.index[0], df_day.index[-1])

    ax_freq = ax_pot.twinx()
    ax_freq.plot(
        df_day.index,
        df_day['freq'],
        color=Colores.VERDE_CLARO,
        label='Frecuencia SENI',
    )
    ax_freq.axhline(
        FRECUENCIA_NOMINAL,
        color=Colores.TURQUESA,
        linestyle='--',
        label='Frecuencia nominal',
    )
    ax_freq.axhline(
        escalon_edac,
        color=Colores.AZUL_OSCURO,
        linestyle='--',
        label='Primer escalón del EDAC',
    )

    for i, evt in enumerate(eventos):
        t = evt['t_min']
        y = evt['generacion'][t]
        pos = (-120, -48) if y > (ymin + y_range * 0.25) else (-120, -20)
        bbox = {'boxstyle': 'round,pad=0.3', 'fc': 'white', 'ec': 'gray'}
        ax_pot.plot(t, y, 'ko')
        ax_freq.axvspan(
            evt['inicio'],
            evt['fin'],
            color=Colores.GRIS_CLARO,
            alpha=0.25,
            label='Evento' if i == 0 else None,
        )
        ax_pot.annotate(
            f'Mínima pendiente\n{evt["p_min"] / 3600:.1f} MW/s',
            xy=(t, y),
            xytext=pos,
            textcoords='offset points',
            arrowprops={'arrowstyle': '-'},
            fontsize=9,
            bbox=bbox,
        )

    ax_freq.set_ylabel('Frecuencia (Hz)')
    ax_freq.tick_params(axis='y')
    ax_pot.grid(True, linestyle='--', alpha=0.5)
    ax_pot.set_ylabel('Potencia (MW)')
    ax_pot.tick_params(axis='y')
    lines1, labels1 = ax_pot.get_legend_handles_labels()
    lines2, labels2 = ax_freq.get_legend_handles_labels()
    ax_pot.legend(
        lines1 + lines2,
        labels1 + labels2,
        loc='lower center',
        bbox_to_anchor=(0.5, -0.15),
        ncol=5,
        frameon=False,
    )
    fig.suptitle(f'Eventos EDAC - {df_day.index[0].date()}')
    plt.tight_layout()

    if pdf is not None:
        pdf.savefig()

    if ruta_archivo is not None:
        plt.savefig(ruta_archivo)
        plt.close(fig)
