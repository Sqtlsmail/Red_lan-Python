from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
import win32security
import win32con
import time
import sys
import ipaddress
import ClientPrueb
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QTextEdit, QMessageBox, QVBoxLayout,
    QHBoxLayout,QSpacerItem, QSizePolicy
)

def validar_credenciales(username, password):
    try:
        token = win32security.LogonUser(
            username,
            None,
            password,
            win32con.LOGON32_LOGON_INTERACTIVE,
            win32con.LOGON32_PROVIDER_DEFAULT
        )
        token.Close()
        return True
    except win32security.error:
        return False

def verificar_codigo_server(codigo):
    try:

        ip = ipaddress.ip_address(codigo)
        return True  
    except ValueError:
        return False   

def verificar_puerto(puerto):
    try:
        puerto = int(puerto)
        if 0 <= puerto <= 65535:
            return True
        else:
            return False
    except ValueError:
         return False
  

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Municipalidad de Chepén - Inicio de Sesion")
        self.setGeometry(100, 100, 400, 300)
        self.setFixedSize(450, 350)

        self.background_label = QLabel(self)
        self.background_label.setScaledContents(True)
        self.set_background_image("images.jpeg")        
        self.load_stylesheet("Login_Client_style.qss")
        
        layout = QVBoxLayout()


        self.label_user = QLabel("Usuario:")
        self.input_user = QLineEdit()


        self.label_password = QLabel("Contraseña:")
        self.input_password = QLineEdit()

        self.label_server = QLabel("Direccion IP:")
        self.input_server = QLineEdit()

        self.label_puerto = QLabel("Puerto:")
        self.input_puerto = QLineEdit()


        self.input_password.setEchoMode(QLineEdit.Password)

        layout.addWidget(self.label_user)
        layout.addWidget(self.input_user)
        layout.addWidget(self.label_password)
        layout.addWidget(self.input_password)
        layout.addWidget(self.label_server)
        layout.addWidget(self.input_server)
        layout.addWidget(self.label_puerto)
        layout.addWidget(self.input_puerto)        

        self.login_button = QPushButton("INGRESAR")
        self.login_button.setObjectName("login_button")
        self.login_button.clicked.connect(self.authenticate)
        layout.addWidget(self.login_button)

        self.Back_button = QPushButton("SALIR")
        self.Back_button.setObjectName("back_button")
        self.Back_button.clicked.connect(self.close_window)
        layout.addWidget(self.Back_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)



    def authenticate(self):
        usuario = self.input_user.text()
        contraseña = self.input_password.text()
        SERVER = self.input_server.text()
        PUERTO = self.input_puerto.text()

        if not PUERTO.isdigit():
            QMessageBox.warning(self, "Error", "El puerto debe ser un número entero.")
            return

        PUERTO = int(PUERTO)

        if not validar_credenciales(usuario, contraseña):
            QMessageBox.warning(self, "Error", "Credenciales incorrectas.")
            return

        if not verificar_codigo_server(SERVER):
            QMessageBox.warning(self, "Error", "Server host incorrecto o mal colocado.")
            return

        if not verificar_puerto(PUERTO):
            QMessageBox.warning(self, "Error", "Número de puerto inválido. Debe estar entre 0 y 65535.")
            return

        try:
            self.client_window = ClientWindow(SERVER,PUERTO,usuario, contraseña)
            if not self.client_window.client.connected:
                self.client_window.close()
                raise ConnectionError("No se pudo conectar al servidor.")
            else:
                self.client_window.show()
                self.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"El servidor no está disponible: {str(e)}")
            return 

        QMessageBox.information(self, "Éxito", "Inicio de sesión exitoso.")

    def set_background_image(self, image_path):
        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            print("Error al cargar la imagen.")
            return
        scaled_pixmap = pixmap.scaled(self.size(), Qt.KeepAspectRatioByExpanding)
        self.background_label.setPixmap(scaled_pixmap)
        self.background_label.setGeometry(self.rect())

    def resizeEvent(self, event):
        """Actualizar el tamaño de la imagen al redimensionar la ventana."""
        self.set_background_image("images.jpeg")
        super().resizeEvent(event)

    def close_window(self):
        self.close()

    def load_stylesheet(self, filename):
        try:
            with open(filename, "r") as file:
                self.setStyleSheet(file.read())
        except FileNotFoundError:
            print(f"No se pudo cargar el archivo {filename}. Verifica la ruta.")    

class ClientWindow(QMainWindow):
    def __init__(self,SERVER,PUERTO, usuario, contraseña):
        super().__init__()

        self.client = ClientPrueb.Client(SERVER,PUERTO,usuario, contraseña)
        self.setWindowTitle(f"Usuario: {self.client.usuario}")
        self.setGeometry(100, 100, 600, 400)

        self.load_stylesheet("Window_Client_Style.qss")
        main_layout = QVBoxLayout()

        text_label_layout = QHBoxLayout()

        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)
        text_label_layout.addWidget(self.text_display)

        self.list_connect = QLabel("Cargando ...")
        self.list_connect.setAlignment(Qt.AlignTop | Qt.AlignLeft)  
        text_label_layout.addWidget(self.list_connect)


        text_label_layout.setContentsMargins(0, 0, 0, 0)
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        text_label_layout.addSpacerItem(spacer)
        main_layout.addLayout(text_label_layout)


        self.input_message = QLineEdit()
        self.input_message.setPlaceholderText("Escribe un mensaje...")
        main_layout.addWidget(self.input_message)

        self.send_button = QPushButton("Enviar")
        self.send_button.clicked.connect(self.send_message)
        main_layout.addWidget(self.send_button)


        self.disconnect_button = QPushButton("Desconectar")
        self.disconnect_button.setObjectName("disconnect_button")
        self.disconnect_button.clicked.connect(self.disconnect)
        main_layout.addWidget(self.disconnect_button)


        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.client_socket = self.client.start()
        self.client.message_received.connect(self.append_message)
        self.client.list_connect_recived.connect(self.append_list_connect)
 
    def send_message(self):
        if self.client_socket and self.client.connected:
            msg = self.input_message.text()
            if msg:
                if msg == self.client.DISCONNECT_MESSAGE:
                    self.disconnect()
                self.client.send(msg, self.client_socket)
                self.input_message.clear()

    def disconnect(self):
        if self.client_socket and self.client.connected:
            self.client.send(self.client.DISCONNECT_MESSAGE, self.client_socket)
            time.sleep(1)
            self.client_socket.close()
            self.client.connected = False
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()

    def append_message(self, message):
        if message == self.client.DISCONNECT_MESSAGE:
            self.disconnect()
        else:
            self.text_display.append(message)

    def append_list_connect(self,list_connect):
        text = f"Conectados:<br>"
        for element in list_connect:
            text += f"{element}<br>"
        self.list_connect.setText(str(text))

    def load_stylesheet(self, filename):
        try:
            with open(filename, "r") as file:
                self.setStyleSheet(file.read())
        except FileNotFoundError:
            print(f"No se pudo cargar el archivo {filename}. Verifica la ruta.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())