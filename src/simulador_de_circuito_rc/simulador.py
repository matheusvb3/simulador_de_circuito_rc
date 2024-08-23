from PyQt5 import QtGui, QtCore
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
    """
    Esta classe gera a janela de interação com o usuário do programa, feita com PyQt5. Não possui nenhum parâmetro passado ao construtor.
    """
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

        layout.addLayout(layout_formulario) # Adiciona o layout de formulário ao layout principal

        botao_gerar_grafico = QPushButton("Gerar gráfico", self)
        botao_gerar_grafico.clicked.connect(self.gerar_grafico)
        layout.addWidget(botao_gerar_grafico)

        self.figura_gerada = plt.figure()
        self.canvas = FigureCanvas(self.figura_gerada)
        layout.addWidget(self.canvas)

        self.botao_salvar = QPushButton("Salvar resultados")
        self.botao_salvar.clicked.connect(self.salvar_resultados)
        self.botao_salvar.setEnabled(False)
        layout.addWidget(self.botao_salvar)

        self.label_fim = QLabel("Gere um gráfico antes de poder ter acesso aos resultados")
        self.label_fim.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.label_fim)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def gerar_grafico(self):
        """
        Gera uma figura com o matplotlib dados os valores V0, R, C, t_final e step_tempo informados pelo usuário.

        :raise ValueError: Caso algum dos valores informados pelo usuário não seja válido (por exemplo, contenha letras) uma mensagem
            de erro será exibida. Esta mensagem também aparecerá se os valores que representam tempo tiverem valores negativos ou nulos
            ou se os dois tiverem o mesmo valor (isso faz com que o matplotlib não consiga gerar o gráfico).
        """
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
        self.botao_salvar.setEnabled(True) # Habilita o botão de salvar os resultados
        self.label_fim.setText("Clique para salvar os resultados como CSV")

    def salvar_resultados(self):
        """
        Salva os resultados obtidos em um arquivo CSV. O nome do arquivo por padrão tem o dia e hora para certificar que não
        tenha possibilidade de haver repetições na hora de salvar.

        :raise Exception: Como sempre pode ocorrer um erro quando pretende-se salvar um arquivo, temos um teste para que seja
            devidamente capturado e apresentado ao usuário.
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
                    self.label_fim.setText("Arquivo salvo com sucesso")

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
    jan.setWindowIcon(QtGui.QIcon('../../images/icon.png'))
    jan.show()
    sys.exit(meu_simulador.exec_())
