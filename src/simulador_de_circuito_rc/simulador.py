from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys

def janela():
    simulador = QApplication(sys.argv)
    jan = QMainWindow()
    jan.setWindowTitle("Simulador de circuito RC")
    jan.show()
    sys.exit(simulador.exec_())

janela()
