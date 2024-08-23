from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt, QTimer, QPointF
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QVBoxLayout, QPushButton, QLabel, QLineEdit
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis
import random
import sys
import numpy as np

def calcula_tensao(V0, R, C, t):
    return V0 * np.exp(-t / (R * C))

def calcula_corrente(V0, R, C, t):
    return (V0 / R) * np.exp(-t / (R * C))

class Simulador(QMainWindow):
    def __init__(self):
        super().__init__()
        self.inicializar_interface()

    def inicializar_interface(self):
        layout = QVBoxLayout()

        self.entrada_R = QLineEdit(self)
        self.entrada_R.setPlaceholderText("Resistência (R) em Ohms")
        layout.addWidget(self.entrada_R)

        self.entrada_C = QLineEdit(self)
        self.entrada_C.setPlaceholderText("Capacitância (C) em Farads")
        layout.addWidget(self.entrada_C)

        self.entrada_V0 = QLineEdit(self)
        self.entrada_V0.setPlaceholderText("Tensão Inicial (V0) em Volts")
        layout.addWidget(self.entrada_V0)

        self.entrada_t_final = QLineEdit(self)
        self.entrada_t_final.setPlaceholderText("Tempo final em segundos")
        layout.addWidget(self.entrada_t_final)

        self.entrada_step_tempo = QLineEdit(self)
        self.entrada_step_tempo.setPlaceholderText("Passo de Tempo em segundos")
        layout.addWidget(self.entrada_step_tempo)

        botao_gerar_grafico = QPushButton("Gerar gráfico", self)
        botao_gerar_grafico.clicked.connect(self.gerar_grafico)
        layout.addWidget(botao_gerar_grafico)

        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        botao_salvar = QPushButton("Salvar resultados")
        botao_salvar.clicked.connect(self.salvar_resultados)
        layout.addWidget(botao_salvar)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def gerar_grafico(self):
        # Obtenha os valores de entrada do usuário
        try:
            R = float(self.entrada_R.text())
            C = float(self.entrada_C.text())
            V0 = float(self.entrada_V0.text())
            t_final = float(self.entrada_t_final.text())
            passo_tempo = float(self.entrada_step_tempo.text())
        except ValueError:
            # Mostre uma mensagem de erro se os valores de entrada não forem válidos
            error_label = QLabel("Por favor, insira valores numéricos válidos.", self)
            error_label.show()
            return

        # Gerar o eixo do tempo
        t = np.arange(0, t_final, passo_tempo)

        # Calcular tensão e corrente
        Vt = calcula_tensao(V0, R, C, t)
        It = calcula_corrente(V0, R, C, t)

        # Limpar o gráfico anterior
        self.figure.clear()

        # Plotar novos dados
        ax = self.figure.add_subplot(111)
        ax.plot(t, Vt, label = "Tensão (V)", c = 'b')
        ax.plot(t, It, label = "Corrente (I)", c = 'r')
        ax.set_xlabel("Tempo (s)")
        ax.set_ylabel("Amplitude")
        ax.set_title("Resposta Transitória do Circuito RC")
        ax.legend()

        # Atualizar o canvas
        self.canvas.draw()

    def salvar_resultados(self):

        pass

if __name__ == '__main__': # Convenção idiomática para se certificar que o programa não está sendo executado importado por algum outro arquivo
    meu_simulador = QApplication(sys.argv)
    jan = Simulador()
    jan.setWindowTitle("Simulador de circuito RC")
    jan.setWindowIcon(QtGui.QIcon('../../icon.png'))
    jan.show()
    sys.exit(meu_simulador.exec_())
