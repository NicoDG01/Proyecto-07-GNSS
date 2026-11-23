# PRGII-PRJ07 — Monitor de Calidad de Recepción GNSS

Aplicación de escritorio en Python (`PySide6` + `Pandas` + `Matplotlib`) para el análisis, limpieza, diagnóstico operativo y visualización temporal de una red de 10 receptores GNSS (`R01` a `R10`).

**Autores:** Ochoa Fernando, Pereyra Martín, De Giglio Nicolás  
**Asignatura:** Programación II (5002) — Ingeniería en Telecomunicaciones (UNRC)

---

## Cambios implementados en `rama-fernando`

Sobre la interfaz base creada en Qt Designer (`AnalizadorGNSS.ui` / `AnalizadorGNSS.py`), se incorporó una arquitectura modular desacoplada:

1. **`procesador_gnss.py` (Back-end):**
   - Carga y validación de `gnss.csv` (`RF-01`).
   - Limpieza de duplicados, detección de valores negativos en `error_m` y tratamiento de estados `SIN_FIX` (`RF-02`, `RF-03`).
   - Cálculo de promedios móviles configurables y métricas estadísticas por receptor (`RF-04`, `RF-05`, `RF-08`).
   - Diagnóstico automático de anomalías: obstrucción progresiva, períodos sin solución, HDOP elevado, ausencia de reportes, mediciones inválidas y picos de error (`RF-07`).
2. **`graficos_gnss.py` (Visualización):**
   - Integración de 3 gráficos temporales sincronizados en `Matplotlib` con barra de herramientas (`NavigationToolbar2QT`): HDOP y Error horizontal, Satélites utilizados y Estado de solución (`RF-06`).
3. **`main.py` (Controlador principal):**
   - Configuración de valores por defecto (`HDOP = 3.0`, `Error = 10.0 m`, `Satélites = 6`, `Ventana = 30`).
   - Tabla resumen con código de colores por estado (`Normal`, `Alerta`, `Crítico`) y barra de estado (`RF-08`, `RF-09`).

---

## Instalación y ejecución en Ubuntu Linux

```bash
# 1. Crear y activar entorno virtual
python3 -m venv venv
source venv/bin/activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar la aplicación
python3 main.py