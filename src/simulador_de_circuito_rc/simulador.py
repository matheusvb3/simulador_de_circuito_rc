from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt, QTimer, QPointF
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QVBoxLayout
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis
import random
import sys

class XYSeriesIODevice:
    QUANT_AMOSTRAS = 200

    def __init__(self, series):
        self.series = series
        self.data = [0] * self.QUANT_AMOSTRAS  # Initialize data with zeroes

    def atualiza_serie(self):
        self.data.pop(0)  # Remove the oldest value
        self.data.append(random.randint(-9, 9))  # Add a new random value

        self.series.clear()
        for i, value in enumerate(self.data):
            self.series.append(QPointF(i, value))

class InputDemo(QWidget):
    FREQ_ATUALIZA_GRAF = 100 # Em milissegundos

    def __init__(self):
        super(InputDemo, self).__init__()

        self.chart = QChart()
        self.series = QLineSeries()
        self.device = XYSeriesIODevice(self.series)

        chartView = QChartView(self.chart)
        chartView.setMinimumSize(600, 400)

        self.chart.addSeries(self.series)

        axisX = QValueAxis()
        axisX.setRange(0, XYSeriesIODevice.QUANT_AMOSTRAS)
        axisX.setLabelFormat('%g')

        axisY = QValueAxis()
        axisY.setRange(-10, 10)  # Set the Y-axis range

        self.chart.addAxis(axisX, Qt.AlignBottom)
        self.series.attachAxis(axisX)
        self.chart.addAxis(axisY, Qt.AlignLeft)
        self.series.attachAxis(axisY)
        self.chart.legend().hide()

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(chartView)
        self.setLayout(mainLayout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.device.atualiza_serie)
        self.timer.start(self.FREQ_ATUALIZA_GRAF)

def janela():
    simulador = QApplication(sys.argv)
    jan = InputDemo()
    jan.setWindowTitle("Simulador de circuito RC")
    jan.setWindowIcon(QtGui.QIcon('../../icon.png'))
    jan.show()
    sys.exit(simulador.exec_())

janela()
