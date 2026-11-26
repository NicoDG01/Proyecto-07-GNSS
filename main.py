"""Punto de entrada y controlador principal de la aplicación PRGII-PRJ07."""

import os
import sys
import pandas as pd
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QBrush, QColor
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QTableWidgetItem,
)

from AnalizadorGNSS import Ui_MainWindow
from graficos_gnss import ContextoGrafico, GestorGraficosGNSS
from procesador_gnss import ParametrosAnalisis, ProcesadorGNSS

NOMBRES_RECEPTORES = {f"R{i:02d}": f"R{i:02d} - Receptor {i}" for i in range(1, 11)}


class VentanaMonitorGNSS(QMainWindow, Ui_MainWindow):
    """Ventana principal del Monitor de Calidad de Recepción GNSS (PRGII-PRJ07)."""

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.resize(1240, 820)

        self.procesador = ProcesadorGNSS()
        self.gestor_graficos = GestorGraficosGNSS(
            self.widget_graf_hdop,
            self.widget_graf_satelites,
            self.widget_graf_estado,
        )
        self.action_acerca_de = QAction("Acerca de...", self)

        self._configurar_controles()
        self._conectar_senales()

        ruta_local = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gnss.csv")
        if os.path.exists(ruta_local):
            self.cargar_archivo(ruta_local)

    def _configurar_controles(self) -> None:
        """Agrega 'Acerca de...' al menú Ayuda (los valores por defecto vienen del .ui)."""
        self.menuAyuda.addAction(self.action_acerca_de)
        self.statusbar.showMessage("Listo. Seleccione un archivo CSV para comenzar.")

    def _conectar_senales(self) -> None:
        """Conecta los eventos de la interfaz con sus métodos manejadores."""
        self.btn_explorar.clicked.connect(self.seleccionar_archivo)
        self.action_abrir_csv.triggered.connect(self.seleccionar_archivo)
        self.action_cerrar.triggered.connect(self.close)
        self.action_acerca_de.triggered.connect(self.mostrar_acerca_de)
        self.btn_analizar.clicked.connect(self.ejecutar_analisis)
        self.combo_receptor.currentIndexChanged.connect(self.actualizar_vista_receptor)

    def _leer_parametros_ui(self) -> ParametrosAnalisis:
        """Obtiene los valores actuales de los controles de umbral y ventana."""
        return ParametrosAnalisis(
            umbral_hdop=self.spin_umbral_hdop.value(),
            umbral_error=self.spin_umbral_error.value(),
            umbral_satelites=self.spin_umbral_satelites.value(),
            ventana_movil=self.spin_ventana_movil.value(),
    )

    def seleccionar_archivo(self) -> None:
        """Abre el diálogo explorador para seleccionar un archivo CSV (RF-01)."""
        ruta, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar archivo de mediciones GNSS",
            "",
            "Archivos CSV (*.csv);;Todos los archivos (*)",
        )
        if ruta:
            self.cargar_archivo(ruta)

    def cargar_archivo(self, ruta: str) -> None:
        """Carga el CSV seleccionado y actualiza el selector de receptores."""
        try:
            self.procesador.cargar_csv(ruta)
            self.txt_archivo.setText(os.path.basename(ruta))

            self.combo_receptor.blockSignals(True)
            self.combo_receptor.clear()
            for rec in sorted(self.procesador.df_limpio["receptor"].unique()):
                self.combo_receptor.addItem(NOMBRES_RECEPTORES.get(rec, rec), userData=rec)
            self.combo_receptor.blockSignals(False)

            self.ejecutar_analisis()
        except (OSError, ValueError, KeyError, pd.errors.ParserError) as exc:
            QMessageBox.critical(
                self,
                "Error al cargar CSV",
                f"No se pudo procesar el archivo seleccionado:\n{exc}",
            )

    def ejecutar_analisis(self) -> None:
        """Ejecuta el análisis completo y refresca informe, tabla y gráficos (RF-05)."""
        if self.procesador.df_limpio is None:
            QMessageBox.warning(
                self,
                "Sin datos",
                "Primero debe cargar un archivo CSV válido.",
            )
            return

        params = self._leer_parametros_ui()
        try:
            self.procesador.analizar(params)
            self._actualizar_informe(params)      # <- ahora recibe params
            self._actualizar_tabla()
            self.actualizar_vista_receptor()

            cant_rec = len(self.procesador.resumen_receptores)
            self.statusbar.showMessage(f"Análisis completo: {cant_rec} receptores procesados")
        except (ValueError, KeyError, RuntimeError) as exc:
            QMessageBox.critical(
                self,
                "Error en el análisis",
                f"Ocurrió un problema durante el cálculo:\n{exc}",
            )

    def _actualizar_informe(self, params: ParametrosAnalisis) -> None:
        """Renderiza el informe diagnóstico y el bloque Calidad GNSS (RF-07)."""
        rep = self.procesador.reporte_limpieza
        problemas = self.procesador.diagnosticos
        cal = self.procesador.calcular_calidad_global(params)

        if problemas:
            items = "".join(
                f"<li><b>{p.split(':', 1)[0]}:</b>{p.split(':', 1)[1]}</li>" for p in problemas
            )
        else:
            items = "<li>Sin anomalías detectadas bajo los umbrales actuales.</li>"

        lineas_calidad = [
            f"Disponibilidad de solución: <b>{cal['disponibilidad']:.1f} %</b>",
            f"HDOP &gt; {params.umbral_hdop:.1f}: <b>{cal['pct_hdop_alto']:.1f} %</b>",
            f"Error &gt; {params.umbral_error:.1f} m: <b>{cal['pct_error_alto']:.1f} %</b>",
            f"Satélites &lt; {params.umbral_satelites}: <b>{cal['pct_sats_bajos']:.1f} %</b>",
            "Receptores Normal / Alerta / Crítico: "
            f"<b>{cal['normal']} / {cal['alerta']} / {cal['critico']}</b>",
        ]
        calidad = "<br>".join(f"• {linea}" for linea in lineas_calidad)

        html = f"""
        <div style="font-family: sans-serif; font-size: 9.5pt;">
            <p style="margin-bottom: 4px;"><b>Receptores con problemas</b></p>
            <ul style="margin-top: 2px; padding-left: 18px;">{items}</ul>
            <hr>
            <p style="margin-bottom: 4px;"><b>Calidad GNSS</b> (% de mediciones de la red)</p>
            <p style="margin: 2px 0; font-size: 8.5pt; color: #333;">{calidad}</p>
            <hr>
            <p style="margin-bottom: 4px;"><b>Preprocesamiento de datos</b></p>
            <p style="margin: 2px 0; font-size: 8.5pt; color: #333;">
                • Registros leídos: <b>{rep.get('total_inicial', 0)}</b><br>
                • Duplicados eliminados: <b>{rep.get('duplicados_eliminados', 0)}</b><br>
                • Mediciones inválidas corregidas: <b>{rep.get('invalidos_corregidos', 0)}</b><br>
                • Registros válidos analizados: <b>{rep.get('total_valido', 0)}</b>
            </p>
        </div>
        """
        self.txt_informe.setHtml(html)

    def _actualizar_tabla(self) -> None:
        """Puebla la tabla resumen con código de colores por estado (RF-08)."""
        datos = self.procesador.resumen_receptores
        self.tabla_resumen.setRowCount(len(datos))

        colores_estado = {
            "Normal": QColor("#d4edda"),
            "Alerta": QColor("#fff3cd"),
            "Crítico": QColor("#f8d7da"),
        }

        for fila, item in enumerate(datos):
            valores = [
                item["receptor"],
                f"{item['hdop_prom']:.2f}",
                f"{item['error_prom']:.2f}",
                f"{item['pct_sin_fix']:.1f}",
                item["estado"],
            ]
            for col, texto in enumerate(valores):
                celda = QTableWidgetItem(texto)
                celda.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if col == 4 and texto in colores_estado:
                    celda.setBackground(QBrush(colores_estado[texto]))
                self.tabla_resumen.setItem(fila, col, celda)

    
    def actualizar_vista_receptor(self) -> None:
        """Actualiza los 3 gráficos temporales para el receptor seleccionado (RF-06)."""
        if self.procesador.df_limpio is None or self.combo_receptor.count() == 0:
            return

        receptor = self.combo_receptor.currentData()
        params = self._leer_parametros_ui()
        df_rec = self.procesador.obtener_datos_receptor(receptor, params.ventana_movil)
        contexto = ContextoGrafico(receptor=receptor, params=params)
        self.gestor_graficos.actualizar_graficos(df_rec, contexto)

    def mostrar_acerca_de(self) -> None:
        """Muestra la ventana modal con información del proyecto y autores."""
        QMessageBox.information(
            self,
            "Acerca de PRGII-PRJ07",
            "Monitor de Calidad de Recepción GNSS\n"
            "Asignatura: Programación II (5002) - Ingeniería en Telecomunicaciones\n"
            "Autores: Ochoa Fernando, Pereyra Martín, De Giglio Nicolás.",
        )


def main() -> None:
    """Inicializa y ejecuta el bucle principal de la interfaz gráfica."""
    app = QApplication(sys.argv)
    ventana = VentanaMonitorGNSS()
    ventana.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
