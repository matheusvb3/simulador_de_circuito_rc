from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QVBoxLayout, QPushButton, QLabel, QLineEdit, QFormLayout, QErrorMessage, QFileDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from lcapy import Circuit
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
        """
        Monta a interface do usuário. A interface é composta por um QFormLayout que é então inserido em um QVBoxLayout. O QFormLayout
        possui cinco QLineEdits (campos de entrada) e seus respectivos QLabels, e o QVBoxLayout possui dois QPushButtons, um canvas
        para mostrar o gráfico associado e um QPixmap (imagem) mostrando o esquemático associado, além de um QLabel trazendo informações
        ao usuário.
        """
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

        botao_gerar_graf_e_esq = QPushButton("Gerar gráfico e esquemático")
        botao_gerar_graf_e_esq.clicked.connect(self.iniciar_simulacao)
        layout.addWidget(botao_gerar_graf_e_esq)

        # As linhas abaixo fazem com que o botão de gerar gráfico seja ativado se for apertado enter enquanto o foco está em um dos campos de entrada
        self.entrada_R.returnPressed.connect(botao_gerar_graf_e_esq.click)
        self.entrada_C.returnPressed.connect(botao_gerar_graf_e_esq.click)
        self.entrada_V0.returnPressed.connect(botao_gerar_graf_e_esq.click)
        self.entrada_t_final.returnPressed.connect(botao_gerar_graf_e_esq.click)
        self.entrada_step_tempo.returnPressed.connect(botao_gerar_graf_e_esq.click)

        self.figura_gerada = plt.figure()
        self.canvas = FigureCanvas(self.figura_gerada)
        self.canvas.setMinimumSize(500, 530)
        layout.addWidget(self.canvas)

        self.esquematico = QLabel(self)
        self.esquematico.adjustSize()
        layout.addWidget(self.esquematico, alignment = Qt.AlignCenter)

        self.botao_salvar = QPushButton("Salvar resultados")
        self.botao_salvar.clicked.connect(self.salvar_resultados)
        self.botao_salvar.setEnabled(False)
        layout.addWidget(self.botao_salvar)

        self.label_fim = QLabel("Gere o gráfico e esquemático antes de poder ter acesso aos resultados")
        layout.addWidget(self.label_fim, alignment = Qt.AlignCenter)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def iniciar_simulacao(self):
        """
        Esta função encapsula as outras duas que formam a simulação do circuito RC. Primeiro é chamada gerar_grafico e posteriormente
        gerar_esquematico. Se gerar_grafico falhar (o que pode ocorrer se, por exemplo, os valores informados pelo usuário não serem
        válidos) nenhuma das linhas seguintes no bloco try serão executadas, e será mostrada uma janela contendo uma mensagem de erro.

        Esta função também troca o cursor do usuário para indicar que está sendo processada a simulação, visto que o uso da classe
        Circuit do pacote lcapy é demorado.
        """
        QApplication.setOverrideCursor(Qt.WaitCursor)

        try:
            self.gerar_grafico()
            self.botao_salvar.setEnabled(True) # Habilita o botão de salvar os resultados
            self.label_fim.setText("Clique para salvar os resultados como CSV")
            self.gerar_esquematico()
        except Exception as e:
            QApplication.restoreOverrideCursor()
            msg_erro = QErrorMessage()
            msg_erro.setWindowTitle("Erro")
            msg_erro.showMessage("Certifique-se de que os valores numéricos inseridos são válidos. O erro que ocorreu é este: " + str(e))
            msg_erro.exec_()
        finally:
            QApplication.restoreOverrideCursor()

    def gerar_grafico(self):
        """
        Gera uma figura com o matplotlib dados os valores V0, R, C, t_final e step_tempo informados pelo usuário.

        :raise ValueError: Se os valores que representam tempo tiverem valores negativos ou nulos  ou se os dois tiverem
            o mesmo valor (isso faz com que o matplotlib não consiga gerar o gráfico).
        """
        R = float(self.entrada_R.text())
        C = float(self.entrada_C.text())
        V0 = float(self.entrada_V0.text())
        t_final = float(self.entrada_t_final.text())
        step_tempo = float(self.entrada_step_tempo.text())
        if t_final <= 0 or step_tempo <= 0 or t_final == step_tempo:
            raise ValueError("os valores de tempo devem ser maiores que zero e não podem ser iguais entre si")

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

    def gerar_esquematico(self):
        """
        Utiliza o pacote lcapy para gerar uma representação esquemática do circuito que está sendo simulado. A imagem é gerada
        a partir de um netlist e é então salva no diretório de imagens e exibida em um QLabel na interface.
        """
        C = float(self.entrada_C.text())
        R = float(self.entrada_R.text())
        V0 = float(self.entrada_V0.text())
        circuito = Circuit(f"""
        W1 1 2; left, size=1.5
        W2 3 4; right, size=1.5
        C 4 1 {C:.3f}; up
        R 2 3 {R:.3f}; down, v={V0:.3g}V
        ; draw_nodes=connections, label_nodes=none""")
        circuito.draw('../../images/circuito_rc.png')
        imagem = QPixmap('../../images/circuito_rc.png')
        imagem = imagem.scaled(300, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.esquematico.setPixmap(imagem)

    def salvar_resultados(self):
        """
        Salva os resultados obtidos em um arquivo CSV. O nome do arquivo por padrão tem o dia e hora para certificar que não
        tenha possibilidade de haver repetições na hora de salvar.

        :raise Exception: Como sempre pode ocorrer um erro quando pretende-se salvar um arquivo, temos um teste para que seja
            devidamente capturado e apresentado ao usuário.
        """
        nome_arquivo = 'resultados_circuito_rc_' + datetime.now().strftime('%d-%m-%Y-%H-%M-%S') + '.csv'
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
