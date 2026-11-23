"""Módulo de visualización gráfica temporal con Matplotlib embebido en PySide6."""

from dataclasses import dataclass
import matplotlib.dates as mdates
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter
from PySide6.QtWidgets import QVBoxLayout

from procesador_gnss import ParametrosAnalisis

DIAS_SEMANA_ES = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]


@dataclass
class ContextoGrafico:
    """Agrupa los parámetros necesarios para renderizar los gráficos de un receptor."""

    receptor: str
    params: ParametrosAnalisis


def _formatear_eje_dias(ax) -> None:
    """Formatea el eje horizontal mostrando los días de la semana en español."""
    ax.xaxis.set_major_locator(mdates.DayLocator())
    ax.xaxis.set_major_formatter(
        FuncFormatter(lambda x, _pos: DIAS_SEMANA_ES[mdates.num2date(x).weekday()])
    )
    ax.grid(True, linestyle="-", alpha=0.25)


class LienzoGrafico:
    """Encapsula una figura Matplotlib y su barra de navegación dentro de un QWidget."""

    def __init__(self, contenedor_widget):
        layout = contenedor_widget.layout()
        if layout is None:
            layout = QVBoxLayout(contenedor_widget)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)

        self.figure = Figure(figsize=(8, 2.2), dpi=96)
        self.figure.patch.set_facecolor("#F5F6F7")
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, contenedor_widget)
        self.toolbar.setMaximumHeight(26)

        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        self.ax = self.figure.add_subplot(111)

    def limpiar(self) -> None:
        """Limpia los ejes actuales y refresca el lienzo."""
        self.ax.clear()
        self.canvas.draw()

    def refrescar(self) -> None:
        """Ajusta márgenes automáticamente y redibuja el gráfico."""
        self.figure.tight_layout(pad=0.6)
        self.canvas.draw()


class GestorGraficosGNSS:
    """Administra los tres gráficos temporales alineados por receptor (RF-06)."""

    def __init__(self, widget_hdop, widget_satelites, widget_estado):
        self.graf_hdop = LienzoGrafico(widget_hdop)
        self.graf_sat = LienzoGrafico(widget_satelites)
        self.graf_est = LienzoGrafico(widget_estado)

    def limpiar_todos(self) -> None:
        """Limpia los tres paneles gráficos."""
        for graf in (self.graf_hdop, self.graf_sat, self.graf_est):
            graf.limpiar()

    def actualizar_graficos(self, df_rec, contexto: ContextoGrafico) -> None:
        """Renderiza las tres series temporales para el receptor activo."""
        if df_rec.empty:
            self.limpiar_todos()
            return

        self._graficar_hdop_error(df_rec, contexto)
        self._graficar_satelites(df_rec, contexto.params)
        self._graficar_estado(df_rec)

    def _graficar_hdop_error(self, df_rec, contexto: ContextoGrafico) -> None:
        """Dibuja la evolución de HDOP y error horizontal con sus umbrales."""
        ax = self.graf_hdop.ax
        ax.clear()
        tiempo = df_rec["timestamp"]
        params = contexto.params

        ax.plot(tiempo, df_rec["hdop_suavizado"], color="#1f77b4", linewidth=1.3, label="HDOP")
        ax.plot(
            tiempo, df_rec["error_suavizado"], color="#ff7f0e", linewidth=1.3, label="Error (m)"
        )
        ax.axhline(
            params.umbral_hdop,
            color="#9467bd",
            linestyle="--",
            linewidth=1.1,
            label=f"Umbral HDOP ({params.umbral_hdop:.1f})",
        )
        ax.axhline(
            params.umbral_error,
            color="#d62728",
            linestyle="--",
            linewidth=1.1,
            label=f"Umbral error ({params.umbral_error:.1f})",
        )
        titulo = (
            f"HDOP y error horizontal del receptor {contexto.receptor} "
            f"(ventana={params.ventana_movil})"
        )
        ax.set_title(titulo, fontsize=10, fontweight="bold")
        ax.set_ylabel("Valor", fontsize=8.5)
        ax.tick_params(labelsize=8)
        ax.legend(loc="upper left", ncol=4, fontsize=7.5, framealpha=0.85)
        _formatear_eje_dias(ax)
        self.graf_hdop.refrescar()

    def _graficar_satelites(self, df_rec, params: ParametrosAnalisis) -> None:
        """Dibuja la cantidad de satélites utilizados y su umbral mínimo."""
        ax = self.graf_sat.ax
        ax.clear()
        tiempo = df_rec["timestamp"]

        ax.plot(
            tiempo, df_rec["satelites_suavizado"], color="#2ca02c", linewidth=1.3, label="Satélites"
        )
        ax.axhline(
            params.umbral_satelites,
            color="#d62728",
            linestyle="--",
            linewidth=1.1,
            label=f"Umbral ({params.umbral_satelites})",
        )
        ax.set_title("Satélites utilizados", fontsize=10, fontweight="bold")
        ax.set_ylabel("Satélites", fontsize=8.5)
        ax.set_ylim(0, max(20, int(df_rec["satelites"].max()) + 2))
        ax.tick_params(labelsize=8)
        ax.legend(loc="lower left", ncol=2, fontsize=7.5, framealpha=0.85)
        _formatear_eje_dias(ax)
        self.graf_sat.refrescar()

    def _graficar_estado(self, df_rec) -> None:
        """Dibuja la evolución escalonada del estado de solución GNSS."""
        ax = self.graf_est.ax
        ax.clear()
        ax.step(
            df_rec["timestamp"],
            df_rec["estado_num"],
            where="post",
            color="#1f77b4",
            linewidth=1.3,
            label="Estado",
        )
        ax.set_yticks([0, 1, 2])
        ax.set_yticklabels(["SIN_FIX", "FIX_2D", "FIX_3D"], fontsize=8)
        ax.set_ylim(-0.3, 2.4)
        ax.set_title("Estado de solución", fontsize=10, fontweight="bold")
        ax.tick_params(axis="x", labelsize=8)
        ax.legend(loc="lower left", fontsize=7.5, framealpha=0.85)
        _formatear_eje_dias(ax)
        self.graf_est.refrescar()