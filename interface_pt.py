from PyQt5 import QtCore, QtWidgets


class Ui_MainWindow(object):

    def setupUi(self, MainWindow):

        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(599, 589)
        MainWindow.setWindowTitle(
            "Central de Mensagens"
        )

        self.centralwidget = QtWidgets.QWidget(
            MainWindow
        )

        # Frame dos botões Enviar/Receber
        self.send_frame = QtWidgets.QFrame(
            self.centralwidget
        )
        self.send_frame.setGeometry(
            QtCore.QRect(20, 310, 561, 80)
        )

        self.push_button_send = QtWidgets.QPushButton(
            self.send_frame
        )
        self.push_button_send.setGeometry(
            QtCore.QRect(10, 10, 261, 61)
        )
        self.push_button_send.setText(
            "Enviar"
        )

        self.push_button_receive = QtWidgets.QPushButton(
            self.send_frame
        )
        self.push_button_receive.setGeometry(
            QtCore.QRect(290, 10, 261, 61)
        )
        self.push_button_receive.setText(
            "Receber"
        )

        # Texto superior
        self.textBrowser = QtWidgets.QTextBrowser(
            self.centralwidget
        )
        self.textBrowser.setGeometry(
            QtCore.QRect(20, 20, 561, 101)
        )

        self.textBrowser.setHtml("""
        <h3>Bem-vindo à Central de Controle</h3>
        <p>
        Aqui você poderá estabelecer conexão com o sistema
        para rotinas de leitura e escrita durante
        o escalonamento de processos.
        </p>
        """)

        # Área de recebimento
        self.receive_frame = QtWidgets.QFrame(
            self.centralwidget
        )
        self.receive_frame.setGeometry(
            QtCore.QRect(20, 410, 561, 131)
        )

        self.label_2 = QtWidgets.QLabel(
            self.receive_frame
        )
        self.label_2.setGeometry(
            QtCore.QRect(20, 10, 151, 17)
        )
        self.label_2.setText(
            "Dados recebidos:"
        )

        self.text_browser_receive = QtWidgets.QTextBrowser(
            self.receive_frame
        )
        self.text_browser_receive.setGeometry(
            QtCore.QRect(20, 30, 521, 71)
        )

        # Status
        self.label_3 = QtWidgets.QLabel(
            self.centralwidget
        )
        self.label_3.setGeometry(
            QtCore.QRect(20, 230, 121, 17)
        )
        self.label_3.setText(
            "Status da Interface:"
        )

        self.text_browser_status = QtWidgets.QTextBrowser(
            self.centralwidget
        )
        self.text_browser_status.setGeometry(
            QtCore.QRect(20, 260, 271, 31)
        )

        # Botão iniciar
        self.push_button_start = QtWidgets.QPushButton(
            self.centralwidget
        )
        self.push_button_start.setGeometry(
            QtCore.QRect(20, 160, 561, 61)
        )
        self.push_button_start.setText(
            "Iniciar"
        )

        # Campo de envio
        self.label = QtWidgets.QLabel(
            self.centralwidget
        )
        self.label.setGeometry(
            QtCore.QRect(310, 230, 151, 17)
        )
        self.label.setText(
            "Dados para envio:"
        )

        self.line_edit_data = QtWidgets.QLineEdit(
            self.centralwidget
        )
        self.line_edit_data.setGeometry(
            QtCore.QRect(310, 260, 271, 29)
        )

        MainWindow.setCentralWidget(
            self.centralwidget
        )