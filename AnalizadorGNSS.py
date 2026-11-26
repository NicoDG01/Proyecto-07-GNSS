# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'AnalizadorGNSS.ui'
##
## Created by: Qt User Interface Compiler version 6.12.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QComboBox, QDoubleSpinBox,
    QFormLayout, QFrame, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QMainWindow, QMenu,
    QMenuBar, QPushButton, QSizePolicy, QSpinBox,
    QStatusBar, QTableWidget, QTableWidgetItem, QTextEdit,
    QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1148, 792)
        self.action_abrir_csv = QAction(MainWindow)
        self.action_abrir_csv.setObjectName(u"action_abrir_csv")
        self.action_cerrar = QAction(MainWindow)
        self.action_cerrar.setObjectName(u"action_cerrar")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.panel_izquierdo = QWidget(self.centralwidget)
        self.panel_izquierdo.setObjectName(u"panel_izquierdo")
        self.panel_izquierdo.setMinimumSize(QSize(260, 0))
        self.panel_izquierdo.setMaximumSize(QSize(280, 16777215))
        self.verticalLayout = QVBoxLayout(self.panel_izquierdo)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.txt_archivo = QLineEdit(self.panel_izquierdo)
        self.txt_archivo.setObjectName(u"txt_archivo")
        self.txt_archivo.setMinimumSize(QSize(35, 25))
        self.txt_archivo.setMaximumSize(QSize(200, 25))
        self.txt_archivo.setReadOnly(True)

        self.horizontalLayout_2.addWidget(self.txt_archivo)

        self.btn_explorar = QPushButton(self.panel_izquierdo)
        self.btn_explorar.setObjectName(u"btn_explorar")
        self.btn_explorar.setMinimumSize(QSize(25, 25))
        self.btn_explorar.setMaximumSize(QSize(35, 35))

        self.horizontalLayout_2.addWidget(self.btn_explorar)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.label = QLabel(self.panel_izquierdo)
        self.label.setObjectName(u"label")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label)

        self.spin_umbral_hdop = QDoubleSpinBox(self.panel_izquierdo)
        self.spin_umbral_hdop.setObjectName(u"spin_umbral_hdop")
        self.spin_umbral_hdop.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.spin_umbral_hdop.setDecimals(1)
        self.spin_umbral_hdop.setMinimum(0.100000000000000)
        self.spin_umbral_hdop.setMaximum(50.000000000000000)
        self.spin_umbral_hdop.setSingleStep(0.500000000000000)
        self.spin_umbral_hdop.setValue(3.000000000000000)

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.spin_umbral_hdop)

        self.label_2 = QLabel(self.panel_izquierdo)
        self.label_2.setObjectName(u"label_2")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_2)

        self.label_3 = QLabel(self.panel_izquierdo)
        self.label_3.setObjectName(u"label_3")

        self.formLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.label_3)

        self.label_4 = QLabel(self.panel_izquierdo)
        self.label_4.setObjectName(u"label_4")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_4)

        self.spin_umbral_error = QDoubleSpinBox(self.panel_izquierdo)
        self.spin_umbral_error.setObjectName(u"spin_umbral_error")
        self.spin_umbral_error.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.spin_umbral_error.setDecimals(1)
        self.spin_umbral_error.setMinimum(0.100000000000000)
        self.spin_umbral_error.setValue(10.000000000000000)

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.spin_umbral_error)

        self.spin_umbral_satelites = QSpinBox(self.panel_izquierdo)
        self.spin_umbral_satelites.setObjectName(u"spin_umbral_satelites")
        self.spin_umbral_satelites.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.spin_umbral_satelites.setMinimum(1)
        self.spin_umbral_satelites.setMaximum(30)
        self.spin_umbral_satelites.setValue(6)

        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.spin_umbral_satelites)

        self.spin_ventana_movil = QSpinBox(self.panel_izquierdo)
        self.spin_ventana_movil.setObjectName(u"spin_ventana_movil")
        self.spin_ventana_movil.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.spin_ventana_movil.setMinimum(1)
        self.spin_ventana_movil.setMaximum(500)
        self.spin_ventana_movil.setValue(30)

        self.formLayout.setWidget(3, QFormLayout.ItemRole.FieldRole, self.spin_ventana_movil)


        self.verticalLayout.addLayout(self.formLayout)

        self.btn_analizar = QPushButton(self.panel_izquierdo)
        self.btn_analizar.setObjectName(u"btn_analizar")

        self.verticalLayout.addWidget(self.btn_analizar)

        self.line = QFrame(self.panel_izquierdo)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout.addWidget(self.line)

        self.label_5 = QLabel(self.panel_izquierdo)
        self.label_5.setObjectName(u"label_5")

        self.verticalLayout.addWidget(self.label_5)

        self.combo_receptor = QComboBox(self.panel_izquierdo)
        self.combo_receptor.setObjectName(u"combo_receptor")

        self.verticalLayout.addWidget(self.combo_receptor)

        self.line_2 = QFrame(self.panel_izquierdo)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.Shape.HLine)
        self.line_2.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout.addWidget(self.line_2)

        self.label_6 = QLabel(self.panel_izquierdo)
        self.label_6.setObjectName(u"label_6")

        self.verticalLayout.addWidget(self.label_6)

        self.txt_informe = QTextEdit(self.panel_izquierdo)
        self.txt_informe.setObjectName(u"txt_informe")
        self.txt_informe.setReadOnly(True)

        self.verticalLayout.addWidget(self.txt_informe)

        self.combo_receptor.raise_()
        self.line.raise_()
        self.label_5.raise_()
        self.line_2.raise_()
        self.label_6.raise_()
        self.txt_informe.raise_()
        self.btn_analizar.raise_()

        self.horizontalLayout.addWidget(self.panel_izquierdo)

        self.panel_derecho = QWidget(self.centralwidget)
        self.panel_derecho.setObjectName(u"panel_derecho")
        self.verticalLayout_2 = QVBoxLayout(self.panel_derecho)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.widget_graf_hdop = QWidget(self.panel_derecho)
        self.widget_graf_hdop.setObjectName(u"widget_graf_hdop")

        self.verticalLayout_2.addWidget(self.widget_graf_hdop)

        self.widget_graf_satelites = QWidget(self.panel_derecho)
        self.widget_graf_satelites.setObjectName(u"widget_graf_satelites")

        self.verticalLayout_2.addWidget(self.widget_graf_satelites)

        self.widget_graf_estado = QWidget(self.panel_derecho)
        self.widget_graf_estado.setObjectName(u"widget_graf_estado")

        self.verticalLayout_2.addWidget(self.widget_graf_estado)

        self.label_7 = QLabel(self.panel_derecho)
        self.label_7.setObjectName(u"label_7")

        self.verticalLayout_2.addWidget(self.label_7)

        self.tabla_resumen = QTableWidget(self.panel_derecho)
        if (self.tabla_resumen.columnCount() < 5):
            self.tabla_resumen.setColumnCount(5)
        __qtablewidgetitem = QTableWidgetItem()
        self.tabla_resumen.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tabla_resumen.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.tabla_resumen.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.tabla_resumen.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.tabla_resumen.setHorizontalHeaderItem(4, __qtablewidgetitem4)
        self.tabla_resumen.setObjectName(u"tabla_resumen")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabla_resumen.sizePolicy().hasHeightForWidth())
        self.tabla_resumen.setSizePolicy(sizePolicy)
        self.tabla_resumen.setMinimumSize(QSize(20, 0))
        self.tabla_resumen.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabla_resumen.setAlternatingRowColors(True)
        self.tabla_resumen.horizontalHeader().setDefaultSectionSize(175)
        self.tabla_resumen.horizontalHeader().setStretchLastSection(True)
        self.tabla_resumen.verticalHeader().setVisible(False)

        self.verticalLayout_2.addWidget(self.tabla_resumen)

        self.verticalLayout_2.setStretch(0, 2)
        self.verticalLayout_2.setStretch(1, 2)
        self.verticalLayout_2.setStretch(2, 2)
        self.verticalLayout_2.setStretch(4, 2)

        self.horizontalLayout.addWidget(self.panel_derecho)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1148, 22))
        self.menuArchivo = QMenu(self.menubar)
        self.menuArchivo.setObjectName(u"menuArchivo")
        self.menuAyuda = QMenu(self.menubar)
        self.menuAyuda.setObjectName(u"menuAyuda")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuArchivo.menuAction())
        self.menubar.addAction(self.menuAyuda.menuAction())
        self.menuArchivo.addAction(self.action_abrir_csv)
        self.menuArchivo.addAction(self.action_cerrar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"PRGII-PRJ07 - Monitor de calidad de recepci\u00f3n GNSS", None))
        self.action_abrir_csv.setText(QCoreApplication.translate("MainWindow", u"Abrir CSV...", None))
#if QT_CONFIG(shortcut)
        self.action_abrir_csv.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+O", None))
#endif // QT_CONFIG(shortcut)
        self.action_cerrar.setText(QCoreApplication.translate("MainWindow", u"Cerrar", None))
#if QT_CONFIG(shortcut)
        self.action_cerrar.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+Q", None))
#endif // QT_CONFIG(shortcut)
        self.txt_archivo.setText("")
        self.btn_explorar.setText(QCoreApplication.translate("MainWindow", u"...", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Umbral HDOP", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Umbral sat\u00e9lites", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Ventana prom. m\u00f3vil", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Umbral error (m)", None))
        self.btn_analizar.setText(QCoreApplication.translate("MainWindow", u"Analizar", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"Receptor a graficar", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"Informe", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"Resumen por receptor", None))
        ___qtablewidgetitem = self.tabla_resumen.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("MainWindow", u"Receptor", None))
        ___qtablewidgetitem1 = self.tabla_resumen.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("MainWindow", u"HDOP prom.", None))
        ___qtablewidgetitem2 = self.tabla_resumen.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("MainWindow", u"Error prom. (m)", None))
        ___qtablewidgetitem3 = self.tabla_resumen.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("MainWindow", u"% sin fix", None))
        ___qtablewidgetitem4 = self.tabla_resumen.horizontalHeaderItem(4)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("MainWindow", u"Estado", None))
        self.menuArchivo.setTitle(QCoreApplication.translate("MainWindow", u"Archivo", None))
        self.menuAyuda.setTitle(QCoreApplication.translate("MainWindow", u"Ayuda", None))
    # retranslateUi

