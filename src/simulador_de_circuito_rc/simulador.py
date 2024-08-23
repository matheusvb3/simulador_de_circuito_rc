from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt, QTimer, QPointF
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QVBoxLayout, QPushButton, QLabel, QLineEdit, QFormLayout, QErrorMessage, QFileDialog
import sys
import numpy as np
import csv
from datetime import datetime

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
        layout_formulario = QFormLayout()

        self.entrada_R = QLineEdit(self)
        layout_formulario.addRow(QLabel("Resistência (R) em Ohms:"), self.entrada_R)

        self.entrada_C = QLineEdit(self)
        layout_formulario.addRow(QLabel("Capacitância (C) em Farads:"), self.entrada_C)

        self.entrada_V0 = QLineEdit(self)
        layout_formulario.addRow(QLabel("Tensão Inicial (V0) em Volts:"), self.entrada_V0)

        self.entrada_t_final = QLineEdit(self)
        layout_formulario.addRow(QLabel("Tempo final em segundoss:"), self.entrada_t_final)

        self.entrada_step_tempo = QLineEdit(self)
        layout_formulario.addRow(QLabel("Passo de Tempo em segundos:"), self.entrada_step_tempo)

        # Adiciona o layout de formulário ao layout principal
        layout.addLayout(layout_formulario)

        botao_gerar_grafico = QPushButton("Gerar gráfico", self)
        botao_gerar_grafico.clicked.connect(self.gerar_grafico)
        layout.addWidget(botao_gerar_grafico)

        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        self.botao_salvar = QPushButton("Salvar resultados")
        self.botao_salvar.clicked.connect(self.salvar_resultados)
        self.botao_salvar.setEnabled(False)
        layout.addWidget(self.botao_salvar)

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
            msg_erro = QErrorMessage()
            msg_erro.setWindowTitle("Erro")
            msg_erro.showMessage("Certifique-se de que os valores numéricos inseridos são válidos")
            msg_erro.exec_()
            return

        # Gerar o eixo do tempo
        self.linha_tempo = np.arange(0, t_final, passo_tempo)

        # Calcular tensão e corrente
        self.V_transiente = calcula_tensao(V0, R, C, self.linha_tempo)
        self.I_transiente = calcula_corrente(V0, R, C, self.linha_tempo)

        # Limpar o gráfico anterior
        self.figure.clear()

        # Plotar novos dados
        ax = self.figure.add_subplot(111)
        ax.plot(self.linha_tempo, self.V_transiente, label = "Tensão (V)", c = 'b')
        ax.plot(self.linha_tempo, self.I_transiente, label = "Corrente (I)", c = 'r')
        ax.set_xlabel("Tempo (s)")
        ax.set_ylabel("Amplitude")
        ax.set_title("Resposta Transitória do Circuito RC")
        ax.legend()

        # Atualizar o canvas
        self.canvas.draw()
        self.botao_salvar.setEnabled(True)

    def salvar_resultados(self):
        # Abrir diálogo para selecionar onde salvar o arquivo
        options = QFileDialog.Options()
        nome_arquivo = 'resultados_circuito_rc_' + datetime.now().strftime("%d-%m-%Y-%H-%M-%S") + '.csv'
        file_path, _ = QFileDialog.getSaveFileName(self, "Salvar resultados", nome_arquivo, "CSV Files (*.csv);;All Files (*)", options=options)

        if file_path:
            try:
                # Salvar os dados em um arquivo CSV
                with open(file_path, mode = 'w', newline = '') as file:
                    writer = csv.writer(file)
                    writer.writerow(["Tempo (s)", "Tensão (V)", "Corrente (I)"])
                    for i in range(len(self.linha_tempo)):
                        writer.writerow([self.linha_tempo[i], self.V_transiente[i], self.I_transiente[i]])

                # Exibir um tooltip de sucesso
                self.entrada_R.setToolTip(f"Resultados salvos em: {file_path}")
                self.entrada_R.setStyleSheet("border: 1px solid green;")
            except Exception as e:
                # Exibir um tooltip de erro
                self.entrada_R.setToolTip(f"Erro ao salvar o arquivo: {str(e)}")
                self.entrada_R.setStyleSheet("border: 1px solid red;")

if __name__ == '__main__': # Convenção idiomática para se certificar que o programa não está sendo executado importado por algum outro arquivo
    meu_simulador = QApplication(sys.argv)
    jan = Simulador()
    jan.setWindowTitle("Simulador de circuito RC")
    jan.setWindowIcon(QtGui.QIcon('../../icon.png'))
    jan.show()
    sys.exit(meu_simulador.exec_())
