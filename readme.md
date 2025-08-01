# Análisis de curvas de generación solar fotovoltaica

Este repositorio contiene los scripts utilizados para el análisis de las curvas
de generación solar fotovoltaica del sistema, con el propósito de analizar su
impacto en la estabilidad de la red y orientar a los operadores de red sobre
cómo deben utilizarse los sistemas de almacenamiento de energía de baterías
(SAEB).

El proyecto incluye lo siguiente:

- Suavizado y remuestreo de la curva de generación.
- Extracción de pendientes máximas y mínimas de generación al inicio y final de
  las curvas.
- Detección y análisis de eventos de actuación del EDAC.

Para fines de presentación, se incluyen también varios gráficos que contienen
la siguiente información:

- Curvas de frecuencia y generación
- Umbral del primer escalón de actuación del EDAC
- Eventos de actuación del EDAC

Los gráficos se exportan individualmente como imágenes PNG y, opcionalmente, un
consolidado en PDF.

## Estructura del proyecto

```txt
curva-erv/
├── src/
│   ├── datos.py        # Carga y preprocesamiento de los datos de entrada
│   ├── suavizado.py    # Suavizado y remuestreo de curvas
│   ├── edac.py         # Detección de eventos EDAC
│   ├── graficas.py     # Generación de gráficos
│   └── utils.py        # Constantes y utilidades
├── main.py             # Script principal para ejecutar el análisis
├── datos/
│   ├── Potencia Activa Centrales ERV.xlsx  # Datos de generación PV
│   └── edac_data.xlsx                      # Datos de EDAC
├── out/
│   ├── pvgen/          # Resultados del análisis de generación PV
│   └── edac/           # Resultados del análisis de eventos del EDAC
└── requirements.txt    # Dependencias del proyecto
```

## Instalación

1. **Clonar el repositorio**
  
  ```ps
  git clone https://github.com/realsebas/curva-erv.git
  cd curva-erv/
  ```

2. **Configurar y activar un entorno virtual (recomendado)**
  Es recomendable instalar un entorno virtual para evitar lidiar con
  instalaciones globales. Es tan sencillo como usar el módulo `venv`:

  ```ps
  python -m venv .venv
  ```
  
  y activarlo (esto cada vez que se vaya a trabajar con el proyecto):
  
  ```ps
  .\.venv\Scripts\activate
  ```

  En Visual Studio Code, con la extensión de Python instalada, los entornos
  virtuales se activan automáticamente, así que este último paso no es
  necesario.
  
3. **Instalar dependencias**
  Con el entorno virtual activado:

  ```ps
  pip install -r requirements.txt
  ```

4. **Verificar los datos de entrada**:
  Es buena idea asegurarse que los archivos `Potencia Activa Centrales ERV.xlsx`
  y `edac_data.xlsx`estén en la carpeta de `datos/`.

## Uso

Ejecuta el script principal para realizar ambos análisis (PV y EDAC):

```bash
python main.py
```

- **Análisis PV**: procesa datos de generación fotovoltaica, genera curvas
  suavizadas en intervalos de 4 s, 1 min, 5 min y 15 min, calcula pendientes
  máximas y mínimas y produce gráficos.

- **Análisis EDAC**: detecta eventos de actuación del EDAC basados en caídas de
  frecuencia y genera gráficos y resúmenes.

## Salidas

- **Análisis PV** (`out/pvgen/`):
  - Subdirectorios por intervalo (`4s`, `1m`, `5m`, `15m`).
  - `graficas.pdf`: gráficos de las curvas por central y día.
  - `pendientes.csv` y `pendientes.xlsx`: resumen de pendientes máximas y
    mínimas.
  - `plots/`: gráficos individuales en PNG.

- **Análisis EDAC** (`out/edac/`):
  - `graficas.pdf`: gráficos de eventos de actuación del EDAC por día.
  - `eventos.xlsx`: resumen de los eventos detectados.
  - `plots/`: gráficos individuales en PNG.

## Notas

- Los colores de los gráficos EDAC están definidos en `utils.py` (clase
  `Colores`). Se utilizó la paleta de colores de la SIE.
- Los parámetros de suavizado y detección de eventos están en
  `suavizado_curvas.py` y `analisis_edac.py`. Probablemente sea buena idea
  ajustarlos a necesidad.
