import os
import sys
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QColor, QBrush
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QTableWidgetItem,
)

from AnalizadorGNSS import Ui_MainWindow
from procesador_gnss import ProcesadorGNSS
from graficos_gnss import GestorGraficosGNSS


NOMBRES_RECEPTORES = {
    f"R{i:02d}": f"R{i:02d} - Receptor {i}" for i in range(1, 11)
}


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

        self._configurar_controles()
        self._conectar_senales()

        # Carga automática si gnss.csv está en el mismo directorio de trabajo
        ruta_local = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gnss.csv")
        if os.path.exists(ruta_local):
            self.cargar_archivo(ruta_local)

    def _configurar_controles(self):
        """Establece los parámetros por defecto definidos en RF-04."""
        # Umbral HDOP (por defecto: 3.0)
        self.spin_umbral_hdop.setRange(0.1, 50.0)
        self.spin_umbral_hdop.setSingleStep(0.5)
        self.spin_umbral_hdop.setValue(3.0)

        # Umbral error (m) (doubleSpinBox_2 en .ui -> por defecto: 10.0)
        self.doubleSpinBox_2.setDecimals(1)
        self.doubleSpinBox_2.setRange(0.1, 100.0)
        self.doubleSpinBox_2.setSingleStep(1.0)
        self.doubleSpinBox_2.setValue(10.0)

        # Umbral satélites (spinBox en .ui -> por defecto: 6)
        self.spinBox.setRange(1, 30)
        self.spinBox.setValue(6)

        # Ventana promedio móvil (spinBox_2 en .ui -> por defecto: 30)
        self.spinBox_2.setRange(1, 500)
        self.spinBox_2.setValue(30)

        # Opción en menú Ayuda
        self.action_acerca_de = QAction("Acerca de...", self)
        self.menuAyuda.addAction(self.action_acerca_de)

        self.statusbar.showMessage("Listo. Seleccione un archivo CSV para comenzar.")

    def _conectar_senales(self):
        self.btn_explorar.clicked.connect(self.seleccionar_archivo)
        self.action_abrir_csv.triggered.connect(self.seleccionar_archivo)
        self.action_cerrar.triggered.connect(self.close)
        self.action_acerca_de.triggered.connect(self.mostrar_acerca_de)
        self.btn_analizar.clicked.connect(self.ejecutar_analisis)
        self.combo_receptor.currentIndexChanged.connect(self.actualizar_vista_receptor)

    def seleccionar_archivo(self):
        ruta, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar archivo de mediciones GNSS",
            "",
            "Archivos CSV (*.csv);;Todos los archivos (*)",
        )
        if ruta:
            self.cargar_archivo(ruta)

    def cargar_archivo(self, ruta: str):
        try:
            self.procesador.cargar_csv(ruta)
            self.txt_archivo.setText(os.path.basename(ruta))

            self.combo_receptor.blockSignals(True)
            self.combo_receptor.clear()
            receptores = sorted(self.procesador.df_limpio["receptor"].unique())
            for rec in receptores:
                etiqueta = NOMBRES_RECEPTORES.get(rec, rec)
                self.combo_receptor.addItem(etiqueta, userData=rec)
            self.combo_receptor.blockSignals(False)

            self.ejecutar_analisis()
        except Exception as exc:
            QMessageBox.critical(
                self,
                "Error al cargar CSV",
                f"No se pudo procesar el archivo seleccionado:\n{exc}",
            )

    def ejecutar_analisis(self):
        if self.procesador.df_limpio is None:
            QMessageBox.warning(
                self,
                "Sin datos",
                "Primero debe cargar un archivo CSV válido.",
            )
            return

        umbral_hdop = self.spin_umbral_hdop.value()
        umbral_error = self.doubleSpinBox_2.value()
        umbral_sat = self.spinBox.value()
        ventana = self.spinBox_2.value()

        try:
            self.procesador.analizar(umbral_hdop, umbral_error, umbral_sat, ventana)
            self._actualizar_informe()
            self._actualizar_tabla()
            self.actualizar_vista_receptor()

            cant_rec = len(self.procesador.resumen_receptores)
            self.statusbar.showMessage(f"Análisis completo: {cant_rec} receptores procesados")
        except Exception as exc:
            QMessageBox.critical(
                self,
                "Error en el análisis",
                f"Ocurrió un problema durante el cálculo:\n{exc}",
            )

    def _actualizar_informe(self):
        """Renderiza el informe diagnóstico en el panel izquierdo (RF-07)."""
        rep = self.procesador.reporte_limpieza
        problemas = self.procesador.diagnosticos

        items_html = ""
        if problemas:
            for p in problemas:
                partes = p.split(":", 1)
                items_html += f"<li><b>{partes[0]}:</b>{partes[1]}</li>"
        else:
            items_html = "<li>Sin anomalías detectadas bajo los umbrales actuales.</li>"

        html = f"""
        <div style="font-family: sans-serif; font-size: 9.5pt;">
            <p style="margin-bottom: 4px;"><b>Receptores con problemas</b></p>
            <ul style="margin-top: 2px; padding-left: 18px;">
                {items_html}
            </ul>
            <hr>
            <p style="margin-bottom: 4px;"><b>Calidad GNSS y Preprocesamiento</b></p>
            <p style="margin: 2px 0; font-size: 8.5pt; color: #333;">
                • Registros leídos: <b>{rep.get('total_inicial', 0)}</b><br>
                • Duplicados eliminados: <b>{rep.get('duplicados_eliminados', 0)}</b><br>
                • Mediciones inválidas corregidas: <b>{rep.get('invalidos_corregidos', 0)}</b><br>
                • Registros válidos analizados: <b>{rep.get('total_valido', 0)}</b>
            </p>
        </div>
        """
        self.txt_informe.setHtml(html)

    def _actualizar_tabla(self):
        """Puebla la tabla resumen con código de colores por estado (RF-08)."""
        datos = self.procesador.resumen_receptores
        self.tabla_resumen.setRowCount(len(datos))

        colores_estado = {
            "Normal": QColor("#d4edda"),   # Verde suave
            "Alerta": QColor("#fff3cd"),   # Amarillo suave
            "Crítico": QColor("#f8d7da"),  # Rojo suave
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

    def actualizar_vista_receptor(self):
        """Actualiza los 3 gráficos temporales para el receptor seleccionado (RF-06)."""
        if self.procesador.df_limpio is None or self.combo_receptor.count() == 0:
            return

        receptor = self.combo_receptor.currentData()
        ventana = self.spinBox_2.value()
        df_rec = self.procesador.obtener_datos_receptor(receptor, ventana)

        self.gestor_graficos.actualizar_graficos(
            df_rec=df_rec,
            receptor=receptor,
            umbral_hdop=self.spin_umbral_hdop.value(),
            umbral_error=self.doubleSpinBox_2.value(),
            umbral_satelites=self.spinBox.value(),
            ventana=ventana,
        )

    def mostrar_acerca_de(self):
        QMessageBox.information(
            self,
            "Acerca de PRGII-PRJ07",
            "Monitor de Calidad de Recepción GNSS\n"
            "Asignatura: Programación II (5002) - Ingeniería en Telecomunicaciones\n"
            "Autores: Ochoa Fernando, Pereyra Martín, De Giglio Nicolás.",
        )


def main():
    app = QApplication(sys.argv)
    ventana = VentanaMonitorGNSS()
    ventana.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()