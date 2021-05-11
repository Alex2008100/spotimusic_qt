import sys, qtmodels
from PyQt5 import QtWidgets

class App(QtWidgets.QMainWindow, qtmodels.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = App()
    window.show()
    app.exec_()
