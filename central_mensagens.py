from PyQt5 import QtWidgets
import sys
import interface_pt
import serial
import time


class CentralMensagens(
    QtWidgets.QMainWindow,
    interface_pt.Ui_MainWindow
):

    def __init__(self, parent=None):

        super(CentralMensagens, self).__init__(parent)

        self.setupUi(self)

        self.arduino = None
        self.connected = False

        self.wait_time = 1

        # Agora trabalhamos com 1 byte
        self.byte_num = 1

        self.received_data = None

        self.sent_values = []
        self.received_values = []

        self.clicked_on_send = 0
        self.clicked_on_receive = 0

        self.text_browser_status.append(
            "Conectado"
            if self.connected
            else "Desconectado"
        )

        # Botões
        self.push_button_send.clicked.connect(
            self.send_data
        )

        self.push_button_receive.clicked.connect(
            self.receive_data
        )

        self.push_button_start.clicked.connect(
            self.begin_serial_connection
        )

    def wait(self, mult=1):

        time.sleep(mult * self.wait_time)

    def set_interface_status(
        self,
        status,
        status_val
    ):

        self.connected = status_val

        self.text_browser_status.clear()

        self.text_browser_status.append(
            status
        )

    def get_input_data(self):

        return str(
            self.line_edit_data.text()
        )

    def write_text_browser(self, msg):

        self.text_browser_receive.append(
            msg
        )

    def read_from_arduino(self):

        try:

            if self.arduino.in_waiting > 0:

                # Lê 1 byte
                data = self.arduino.read(1)

                if data:

                    # Converte byte para decimal
                    valor = int.from_bytes(
                        data,
                        byteorder='big'
                    )

                    self.received_data = str(
                        valor
                    )

                    self.wait()

        except Exception as err:

            print(
                "Falha ao receber dados!"
            )

            print(err)

    def write_to_arduino(self, msg):

        try:

            valor = int(msg)

            if valor < 0 or valor > 255:

                self.write_text_browser(
                    "Valor deve estar "
                    "entre 0 e 255!"
                )

                return

            # Envia 1 byte binário
            self.arduino.write(
                bytes([valor])
            )

            self.wait()

        except Exception as err:

            print(
                "Falha ao enviar dados!"
            )

            print(err)

    def receive_data(self):

        if self.connected:

            self.read_from_arduino()

            if self.received_data:

                self.clicked_on_receive += 1

                self.received_values.append(
                    self.received_data
                )

                msg = (
                    f"Dados recebidos: "
                    f"{self.received_data}"
                )

            else:

                msg = (
                    "Nenhum dado recebido."
                )

        else:

            msg = (
                "Central não conectada "
                "ao sistema!"
            )

        self.write_text_browser(msg)

    def send_data(self):

        if self.connected:

            data = self.get_input_data()

            if data.isdigit():

                valor = int(data)

                if valor >= 0 and valor <= 255:

                    self.clicked_on_send += 1

                    self.sent_values.append(
                        str(valor)
                    )

                    self.write_to_arduino(
                        str(valor)
                    )

                    msg = (
                        f"Central enviou "
                        f"{valor} ao sistema"
                    )

                else:

                    msg = (
                        "Valor deve estar "
                        "entre 0 e 255!"
                    )

            else:

                msg = (
                    "Somente números "
                    "inteiros podem "
                    "ser enviados!"
                )

        else:

            msg = (
                "Central não conectada "
                "ao sistema!"
            )

        self.write_text_browser(msg)

    def begin_serial_connection(self):

        msg = (
            "Iniciando conexão serial..."
        )

        try:

            self.write_text_browser(msg)

            # TROQUE A COM SE NECESSÁRIO
            self.arduino = serial.Serial(
                'COM11',
                9600,
                timeout=1
            )

            self.wait(2)

            status = True

        except Exception as err:

            print("Falha na conexão!")
            print(err)

            status = False

        if status:

            interface_status = "Conectado"

            msg = (
                "Conexão serial "
                "estabelecida!"
            )

        else:

            interface_status = "Desconectado"

            msg = (
                "Não foi possível "
                "conectar!"
            )

        self.set_interface_status(
            interface_status,
            status
        )

        self.write_text_browser(msg)

        self.sent_values.clear()
        self.received_values.clear()

        self.received_data = None

    # Fecha porta serial corretamente
    def closeEvent(self, event):

        if self.arduino:

            self.arduino.close()

        event.accept()


def main():

    app = QtWidgets.QApplication(
        sys.argv
    )

    window = CentralMensagens()

    window.show()

    sys.exit(
        app.exec_()
    )


if __name__ == '__main__':
    main()