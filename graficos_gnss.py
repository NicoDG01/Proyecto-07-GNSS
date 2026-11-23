import matplotlib
matplotlib.use("QtAgg")

import matplotlib.dates as mdates
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from PySide6.QtWidgets import QVBoxLayout


DIAS_SEMANA_ES = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]


def _formatear_eje_dias(ax):
    """Formatea el eje temporal mostrando los días de la semana en español."""
    ax.xaxis.set_major_locator(mdates.DayLocator())
    ax.xaxis.set_major_formatter(
        matplotlib.ticker.FuncFormatter(
            lambda x, pos: DIAS_SEMANA_ES[mdates.num2date(x).weekday()]
        )
    )
    ax.grid(True, linestyle="-", alpha=0.25)


class LienzoGrafico:
    """Encapsula una figura Matplotlib y su barra de herramientas dentro de un QWidget."""

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


class GestorGraficosGNSS:
    """Administra los tres gráficos temporales alineados por receptor (RF-06)."""

    def __init__(self, widget_hdop, widget_satelites, widget_estado):
        self.graf_hdop = LienzoGrafico(widget_hdop)
        self.graf_sat = LienzoGrafico(widget_satelites)
        self.graf_est = LienzoGrafico(widget_estado)

    def limpiar_todos(self):
        for g in (self.graf_hdop, self.graf_sat, self.graf_est):
            g.ax.clear()
            g.canvas.draw()

    def actualizar_graficos(
        self,
        df_rec,
        receptor: str,
        umbral_hdop: float,
        umbral_error: float,
        umbral_satelites: int,
        ventana: int,
    ):
        if df_rec.empty:
            self.limpiar_todos()
            return

        t = df_rec["timestamp"]

        # --- Gráfico 1: HDOP y Error Horizontal ---
        ax1 = self.graf_hdop.ax
        ax1.clear()
        ax1.plot(t, df_rec["hdop_suavizado"], color="#1f77b4", linewidth=1.3, label="HDOP")
        ax1.plot(t, df_rec["error_suavizado"], color="#ff7f0e", linewidth=1.3, label="Error (m)")
        ax1.axhline(umbral_hdop, color="#9467bd", linestyle="--", linewidth=1.1, label=f"Umbral HDOP ({umbral_hdop:.1f})")
        ax1.axhline(umbral_error, color="#d62728", linestyle="--", linewidth=1.1, label=f"Umbral error ({umbral_error:.1f})")
        ax1.set_title(f"HDOP y error horizontal del receptor {receptor} (ventana={ventana})", fontsize=10, fontweight="bold")
        ax1.set_ylabel("Valor", fontsize=8.5)
        ax1.tick_params(labelsize=8)
        ax1.legend(loc="upper left", ncol=4, fontsize=7.5, framealpha=0.85)
        _formatear_eje_dias(ax1)
        self.graf_hdop.figure.tight_layout(pad=0.6)
        self.graf_hdop.canvas.draw()

        # --- Gráfico 2: Satélites utilizados ---
        ax2 = self.graf_sat.ax
        ax2.clear()
        ax2.plot(t, df_rec["satelites_suavizado"], color="#2ca02c", linewidth=1.3, label="Satélites")
        ax2.axhline(umbral_satelites, color="#d62728", linestyle="--", linewidth=1.1, label=f"Umbral ({umbral_satelites})")
        ax2.set_title("Satélites utilizados", fontsize=10, fontweight="bold")
        ax2.set_ylabel("Satélites", fontsize=8.5)
        ax2.set_ylim(0, max(20, int(df_rec["satelites"].max()) + 2))
        ax2.tick_params(labelsize=8)
        ax2.legend(loc="lower left", ncol=2, fontsize=7.5, framealpha=0.85)
        _formatear_eje_dias(ax2)
        self.graf_sat.figure.tight_layout(pad=0.6)
        self.graf_sat.canvas.draw()

        # --- Gráfico 3: Estado de solución GNSS ---
        ax3 = self.graf_est.ax
        ax3.clear()
        ax3.step(t, df_rec["estado_num"], where="post", color="#1f77b4", linewidth=1.3, label="Estado")
        ax3.set_yticks([0, 1, 2])
        ax3.set_yticklabels(["SIN_FIX", "FIX_2D", "FIX_3D"], fontsize=8)
        ax3.set_ylim(-0.3, 2.4)
        ax3.set_title("Estado de solución", fontsize=10, fontweight="bold")
        ax3.tick_params(axis="x", labelsize=8)
        ax3.legend(loc="lower left", fontsize=7.5, framealpha=0.85)
        _formatear_eje_dias(ax3)
        self.graf_est.figure.tight_layout(pad=0.6)
        self.graf_est.canvas.draw()