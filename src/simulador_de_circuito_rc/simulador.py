from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QVBoxLayout, QPushButton, QLabel, QLineEdit, QFormLayout, QErrorMessage, QFileDialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import sys
import numpy as np
import csv
from datetime import datetime

def calcular_tensao(V0: float, R: float, C: float, t: float) -> float:
    """
    Calcula o valor de tensão do circuito RC em um instante t dados V0, R e C.

    :param V0: Tensão inicial em Volts.
    :param R: Valor do resistor em Ohms.
    :param C: Valor da capacitância em Farads.
    :param t: Instante de tempo em segundos.
    :return: Valor de tensão em Volts.
    """
    return V0 * np.exp(-t / (R * C))

def calcular_corrente(V0: float, R: float, C: float, t: float) -> float:
    """
    Calcula o valor de corrente do circuito RC em um instante t dados V0, R e C.

    :param V0: Tensão inicial em Volts.
    :param R: Valor do resistor em Ohms.
    :param C: Valor da capacitância em Farads.
    :param t: Instante de tempo em segundos.
    :return: Valor de corrente em Amperes.
    """
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
        layout_formulario.addRow(QLabel("Tempo final em segundos:"), self.entrada_t_final)

        self.entrada_step_tempo = QLineEdit(self)
        layout_formulario.addRow(QLabel("Passo de tempo em segundos:"), self.entrada_step_tempo)

        # Adiciona o layout de formulário ao layout principal
        layout.addLayout(layout_formulario)

        botao_gerar_grafico = QPushButton("Gerar gráfico", self)
        botao_gerar_grafico.clicked.connect(self.gerar_grafico)
        layout.addWidget(botao_gerar_grafico)

        self.figura_gerada = plt.figure()
        self.canvas = FigureCanvas(self.figura_gerada)
        layout.addWidget(self.canvas)

        self.botao_salvar = QPushButton("Salvar resultados")
        self.botao_salvar.clicked.connect(self.salvar_resultados)
        self.botao_salvar.setEnabled(False)
        self.botao_salvar.setToolTip("Gere um gráfico antes de ter acesso aos resultados")
        layout.addWidget(self.botao_salvar)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def gerar_grafico(self):
        try:
            R = float(self.entrada_R.text())
            C = float(self.entrada_C.text())
            V0 = float(self.entrada_V0.text())
            t_final = float(self.entrada_t_final.text())
            step_tempo = float(self.entrada_step_tempo.text())
            if t_final <= 0 or step_tempo <= 0 or t_final == step_tempo:
                raise ValueError
        except ValueError:
            msg_erro = QErrorMessage()
            msg_erro.setWindowTitle("Erro")
            msg_erro.showMessage("Certifique-se de que os valores numéricos inseridos são válidos.")
            msg_erro.exec_()
            return

        self.linha_tempo = np.arange(0, t_final, step_tempo)

        self.V_transiente = calcular_tensao(V0, R, C, self.linha_tempo)
        self.I_transiente = calcular_corrente(V0, R, C, self.linha_tempo)

        self.figura_gerada.clear() # Limpa o gráfico que tenha sido gerado anteriormente

        graf = self.figura_gerada.add_subplot(111)
        graf.plot(self.linha_tempo, self.V_transiente, label = "Tensão (V)", c = 'b')
        graf.plot(self.linha_tempo, self.I_transiente, label = "Corrente (A)", c = 'r')
        graf.set_xlabel("Tempo (s)")
        graf.set_ylabel("Amplitude")
        graf.set_title("Resposta transitória do circuito RC")
        graf.grid()
        graf.legend()

        self.canvas.draw()
        self.botao_salvar.setEnabled(True) # Habilita o botão de salvar os resultados e remove o seu tooltip
        self.botao_salvar.setToolTip("")

    def salvar_resultados(self):
        """
        Converte a temperatura de Celsius para Fahrenheit.

        :param temp_celsius: Temperatura em Celsius.
        :return: Temperatura em Fahrenheit.
        :raise Exception: Apenas para certificar-se de que o salvamento do arquivo tenha ocorrido com sucesso, é realizado um teste.
        """
        nome_arquivo = 'resultados_circuito_rc_' + datetime.now().strftime("%d-%m-%Y-%H-%M-%S") + '.csv'
        caminho_arquivo, _ = QFileDialog.getSaveFileName(self, "Salvar resultados", nome_arquivo, "CSV Files (*.csv);;All Files (*)")
        # Na linha acima, _ é usado como uma convenção idiomática para indicar que o valor retornado não será útil e pode ser descartado.
        # O segundo valor retornado por getSaveFileName é o filtro utilizado (neste caso, .csv).

        if caminho_arquivo:
            try:
                # O argumento newline de open faz com que não seja inserido nenhum caracter de fim de linha no arquivo a ser escrito
                with open(caminho_arquivo, mode = 'w', newline = '') as arquivo:
                    writer = csv.writer(arquivo)
                    writer.writerow(["Tempo (s)", "Tensão (V)", "Corrente (A)"])
                    for i in range(len(self.linha_tempo)):
                        writer.writerow([self.linha_tempo[i], self.V_transiente[i], self.I_transiente[i]])

            except Exception as e:
                msg_erro = QErrorMessage()
                msg_erro.setWindowTitle("Erro")
                msg_erro.showMessage("Ocorreu erro ao salvar o arquivo com os resultados. O erro é este: " + str(e))
                msg_erro.exec_()
                return

if __name__ == '__main__': # Convenção idiomática para se certificar que o programa não está sendo executado importado por algum outro arquivo
    meu_simulador = QApplication(sys.argv)
    jan = Simulador()
    jan.setWindowTitle("Simulador de circuito RC")
    jan.setWindowIcon(QtGui.QIcon('../../icon.png'))
    jan.show()
    sys.exit(meu_simulador.exec_())
