from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets


class Ui_MainWindow(object):

    def setupUi(self, MainWindow):

        MainWindow.setObjectName(
            "MainWindow"
        )

        MainWindow.resize(
            1100,
            800
        )

        MainWindow.setWindowTitle(
            "BM32OS"
        )

        self.centralwidget = QtWidgets.QWidget(
            MainWindow
        )

        MainWindow.setCentralWidget(
            self.centralwidget
        )

        #
        # LAYOUT PRINCIPAL
        #

        self.verticalLayout = (
            QtWidgets.QVBoxLayout(
                self.centralwidget
            )
        )

        #
        # TITULO
        #

        self.label_title = QtWidgets.QLabel()

        self.label_title.setAlignment(
            QtCore.Qt.AlignCenter
        )

        self.label_title.setText(
            "BM32OS - Interface de Controle"
        )

        font_title = QtGui.QFont()

        font_title.setPointSize(
            16
        )

        font_title.setBold(
            True
        )

        self.label_title.setFont(
            font_title
        )

        self.verticalLayout.addWidget(
            self.label_title
        )
        #
        # LCD VIRTUAL
        #

        self.group_lcd = QtWidgets.QGroupBox(
            "LCD Virtual"
        )

        self.group_lcd_layout = (
            QtWidgets.QVBoxLayout(
                self.group_lcd
            )
        )

        self.label_lcd = QtWidgets.QLabel()

        self.label_lcd.setMinimumHeight(
            100
        )

        self.label_lcd.setAlignment(
            QtCore.Qt.AlignCenter
        )

        self.label_lcd.setWordWrap(
            True
        )

        self.label_lcd.setText(
            "Aguardando dados..."
        )

        self.group_lcd_layout.addWidget(
            self.label_lcd
        )

        self.verticalLayout.addWidget(
            self.group_lcd
        )

        #
        # DISPLAYS FPGA
        #

        self.group_display = QtWidgets.QGroupBox(
            "Displays FPGA"
        )

        self.display_layout = (
            QtWidgets.QHBoxLayout(
                self.group_display
            )
        )

        font_display = QtGui.QFont()

        font_display.setPointSize(
            24
        )

        font_display.setBold(
            True
        )

        self.display_1 = QtWidgets.QLabel(
            "0"
        )

        self.display_1.setAlignment(
            QtCore.Qt.AlignCenter
        )

        self.display_1.setFont(
            font_display
        )

        self.display_layout.addWidget(
            self.display_1
        )

        self.display_2 = QtWidgets.QLabel(
            "0"
        )

        self.display_2.setAlignment(
            QtCore.Qt.AlignCenter
        )

        self.display_2.setFont(
            font_display
        )

        self.display_layout.addWidget(
            self.display_2
        )

        self.display_3 = QtWidgets.QLabel(
            "0"
        )

        self.display_3.setAlignment(
            QtCore.Qt.AlignCenter
        )

        self.display_3.setFont(
            font_display
        )

        self.display_layout.addWidget(
            self.display_3
        )

        self.display_4 = QtWidgets.QLabel(
            "0"
        )

        self.display_4.setAlignment(
            QtCore.Qt.AlignCenter
        )

        self.display_4.setFont(
            font_display
        )

        self.display_layout.addWidget(
            self.display_4
        )

        self.verticalLayout.addWidget(
            self.group_display
        )
        #
        # BOTAO CONECTAR
        #

        self.push_button_start = (
            QtWidgets.QPushButton(
                "Conectar ao Sistema"
            )
        )

        self.verticalLayout.addWidget(
            self.push_button_start
        )

        #
        # ENTRADA NUMERICA
        #

        self.group_numeric = QtWidgets.QGroupBox(
            "Entrada Numérica"
        )

        self.group_numeric_layout = (
            QtWidgets.QHBoxLayout(
                self.group_numeric
            )
        )

        self.line_edit_number = (
            QtWidgets.QLineEdit()
        )

        self.line_edit_number.setPlaceholderText(
            "Digite um valor entre 0 e 255"
        )

        self.group_numeric_layout.addWidget(
            self.line_edit_number
        )

        self.push_button_send_number = (
            QtWidgets.QPushButton(
                "OK"
            )
        )

        self.group_numeric_layout.addWidget(
            self.push_button_send_number
        )

        self.verticalLayout.addWidget(
            self.group_numeric
        )

        #
        # ENTRADA TEXTO
        #

        self.group_text = QtWidgets.QGroupBox(
            "Nome do Arquivo"
        )

        self.group_text_layout = (
            QtWidgets.QHBoxLayout(
                self.group_text
            )
        )

        self.line_edit_text = (
            QtWidgets.QLineEdit()
        )

        self.line_edit_text.setPlaceholderText(
            "Digite o nome do arquivo"
        )

        self.group_text_layout.addWidget(
            self.line_edit_text
        )

        self.push_button_save_name = (
            QtWidgets.QPushButton(
                "Salvar Nome"
            )
        )

        self.group_text_layout.addWidget(
            self.push_button_save_name
        )

        self.verticalLayout.addWidget(
            self.group_text
        )
        #
        # TABELA DE PROGRAMAS
        #

        self.group_programs = QtWidgets.QGroupBox(
            "Programas"
        )

        self.group_programs_layout = (
            QtWidgets.QVBoxLayout(
                self.group_programs
            )
        )

        self.table_programs = (
            QtWidgets.QTableWidget()
        )

        self.table_programs.setRowCount(
            10
        )

        self.table_programs.setColumnCount(
            2
        )

        self.table_programs.setHorizontalHeaderLabels(
            [
                "ID",
                "Nome"
            ]
        )

        self.table_programs.horizontalHeader().setStretchLastSection(
            True
        )

        self.table_programs.verticalHeader().setVisible(
            False
        )

        self.table_programs.setEditTriggers(
            QtWidgets.QAbstractItemView.NoEditTriggers
        )

        self.table_programs.setSelectionMode(
            QtWidgets.QAbstractItemView.NoSelection
        )

        self.group_programs_layout.addWidget(
            self.table_programs
        )

        self.verticalLayout.addWidget(
            self.group_programs
        )

        #
        # STATUS
        #

        self.group_status = QtWidgets.QGroupBox(
            "Status da Conexão"
        )

        self.group_status_layout = (
            QtWidgets.QVBoxLayout(
                self.group_status
            )
        )

        self.text_browser_status = (
            QtWidgets.QTextBrowser()
        )

        self.text_browser_status.setMaximumHeight(
            80
        )

        self.group_status_layout.addWidget(
            self.text_browser_status
        )

        self.verticalLayout.addWidget(
            self.group_status
        )
        #
        # LOG UART
        #

        self.group_log = QtWidgets.QGroupBox(
            "Histórico UART"
        )

        self.group_log_layout = (
            QtWidgets.QVBoxLayout(
                self.group_log
            )
        )

        self.text_browser_receive = (
            QtWidgets.QTextBrowser()
        )

        self.group_log_layout.addWidget(
            self.text_browser_receive
        )

        self.verticalLayout.addWidget(
            self.group_log
        )

        #
        # FINALIZACAO
        #

        self.retranslateUi(
            MainWindow
        )

        QtCore.QMetaObject.connectSlotsByName(
            MainWindow
        )

    def retranslateUi(self, MainWindow):

        MainWindow.setWindowTitle(
            "BM32OS"
        )
