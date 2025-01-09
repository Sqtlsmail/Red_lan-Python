import threading 
from threading import Lock
import Servidor
import sys
from PyQt5.QtGui import QPixmap
import ipaddress
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QMessageBox,QApplication, QMainWindow, QTextEdit, QPushButton, QVBoxLayout, QWidget, QLabel, QLineEdit,QHBoxLayout


class UserWindow(QMainWindow):
    def __init__(self, user):
        self.user = user
        self.Disconnect_state = False
        self.state_close_process = False

        super().__init__()
        self.setWindowTitle(f"User: {self.user.Adrr[0]}")

        self.setWindowFlags(
            Qt.Window |
            Qt.WindowTitleHint |
            Qt.WindowSystemMenuHint |
            Qt.CustomizeWindowHint
        )

        self.label_name = QLabel("Usuario: NONE")
        self.label_info_CPU = QLabel("CPU: NONE")
        self.label_info_Memoria = QLabel("Memoria: NONE")
        self.label_info_Disc = QLabel("Disco: NONE")

    
        self.system_info_layout = QHBoxLayout()
        self.system_info_layout.addWidget(self.label_info_CPU)
        self.system_info_layout.addWidget(self.label_info_Memoria)
        self.system_info_layout.addWidget(self.label_info_Disc)

 
        self.label_info_Procesos = QLabel("PROCESOS")
        self.text_log = QTextEdit()
        self.text_log.setReadOnly(True)

        self.text_process = QLineEdit()
        self.text_process.setPlaceholderText("Escribe un Proceso a Cerrar...")
        self.close_process_user = QPushButton("CERRAR PROCESO")
        self.close_process_user.clicked.connect(self.Active_close_process)

        self.Disconnect_user = QPushButton("DESCONECTAR")
        self.Disconnect_user.clicked.connect(self.disconnect)

        layout = QVBoxLayout()
        layout.addWidget(self.label_name)
        layout.addLayout(self.system_info_layout)  
        layout.addWidget(self.label_info_Procesos)
        layout.addWidget(self.text_log)
        layout.addWidget(self.text_process)
        layout.addWidget(self.close_process_user)
        layout.addWidget(self.Disconnect_user)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.User_name()
        self.refresh_procesos()
        self.refresh_System()

    def refresh_System(self):
        """Actualiza la información del sistema del usuario."""
        if isinstance(self.user.system_data, dict) and self.user.system_data:
            self.label_info_CPU.setText(
                f"<b>CPU</b><br>"
                f"Uso Total: {self.user.system_data['cpu']['Uso_Total_CPU']}<br>"
                f"Velocidad: {self.user.system_data['cpu']['Velocidad_CPU_GHz']} GHz"
            )

            self.label_info_Memoria.setText(
                f"<b>Memoria</b><br>"
                f"En uso: {self.user.system_data['memory']['Memoria_en_uso']}/{self.user.system_data['memory']['Total_Memoria']}<br>"
                f"Velocidad: {self.user.system_data['memory']['Velocidad']}"
            )

            self.label_info_Disc.setText(
                f"<b>Disco</b><br>"
                f"En uso: {self.user.system_data['disk_data']['Espacio_Utilizado']}/{self.user.system_data['disk_data']['Total_Disco']}<br>"
                f"Tiempo de Actividad: {self.user.system_data['disk_info']['Tiempo_Actividad']} ms<br>"
                f"Velocidad de Lectura: {self.user.system_data['disk_info']['Velocidad_Lectura_KBps']} KBps"
            )


    def refresh_procesos(self):
        text_process = ""
        for proceso in self.user.procesos:
            text_process += (f"<pre>ID: {proceso.get('PID', 'N/A'):>6} | "
                                   f"Nombre: {proceso.get('Nombre', 'N/A'):<20} | "
                                   f"Uso CPU: {proceso.get('CPU (%)', 0):<5}% | "
                                   f"Memoria RSS: {proceso.get('Memoria RSS (MB)', 0.0):<10.2f} MB | "
                                   f"Memoria VMS: {proceso.get('Memoria VMS (MB)', 0.0):<10.2f} MB </pre>")
        self.text_log.setText(text_process)        


    def User_name(self):
        self.label_name.setText(f"Usuario: {self.user.name}")

    def disconnect(self):
        self.Disconnect_state = True
        self.close()
    
    def close_window(self):
        self.close()    

    def get_process_to_close(self):
        return self.text_process.text()   
    
    def Active_close_process(self):
        if self.text_process.text() != "":
            self.state_close_process = True

    def update_user(self, user):
        self.user = user
        self.refresh_procesos()
        self.refresh_System()
        self.User_name()

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

class Create_Server(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Server") 
        self.setGeometry(100,100,400,300)
        self.setFixedSize(400,300)

        self.background_label = QLabel(self)
        self.background_label.setScaledContents(True)
        self.set_background_image("images.jpeg")        
        self.load_stylesheet("Window_Server_style.qss")

        layout = QVBoxLayout()

        self.label_Server_connection = QLabel("Direccion IP:")
        self.input_Server_connection = QLineEdit()
          
        self.label_Port_connection = QLabel("Puerto:")
        self.input_Port_connection = QLineEdit()

        layout.addWidget(self.label_Server_connection)
        layout.addWidget(self.input_Server_connection)
        layout.addWidget(self.label_Port_connection)
        layout.addWidget(self.input_Port_connection)

        self.Create_Server = QPushButton("Crear Servidor")
        self.Create_Server.setObjectName("start_Server")
        self.Create_Server.clicked.connect(self.authenticate)
        layout.addWidget(self.Create_Server)
        self.back_windows = QPushButton("Salir")
        self.back_windows.setObjectName("back_windows")
        self.back_windows.clicked.connect(self.close_window)
        layout.addWidget(self.back_windows)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def authenticate(self):
        SERVER = self.input_Server_connection.text()
        PUERTO = self.input_Port_connection.text()

        if not PUERTO.isdigit():
            QMessageBox.warning(self, "Error", "El puerto debe ser un número entero.")
            return

        PUERTO = int(PUERTO)        

        if not verificar_codigo_server(SERVER):
            QMessageBox.warning(self, "Error", "Server host incorrecto o mal colocado.")
            return

        if not verificar_puerto(PUERTO):
            QMessageBox.warning(self, "Error", "Número de puerto inválido. Debe estar entre 0 y 65535.")
            return

        QMessageBox.information(self, "Éxito", "Inicio de sesión exitoso.")
        self.open_server_window(PUERTO,SERVER)


    def open_server_window(self,PUERTO, SERVER):
        self.server_window = ServerApp(PUERTO,SERVER)
        self.server_window.show()
        self.close()

    def set_background_image(self, image_path):
        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            print("Error al cargar la imagen.")
            return
        scaled_pixmap = pixmap.scaled(self.size(), Qt.KeepAspectRatioByExpanding)
        self.background_label.setPixmap(scaled_pixmap)
        self.background_label.setGeometry(self.rect())

    def load_stylesheet(self, filename):
        try:
            with open(filename, "r") as file:
                self.setStyleSheet(file.read())
        except FileNotFoundError:
            print(f"No se pudo cargar el archivo {filename}. Verifica la ruta.")    


    def close_window(self):
        self.close()
            

class ServerApp(QMainWindow):
    log_signal = pyqtSignal(str)
    new_client_signal = pyqtSignal(object)
    update_client_signal = pyqtSignal(object)
    
    def __init__(self,PUERTO,SERVER):
        super().__init__()
        self.setWindowTitle("Server Control Panel")

        self.load_stylesheet("Window_Server_Control_style.qss")

        self.text_log = QTextEdit()
        self.text_log.setReadOnly(True)

        self.btn_start = QPushButton("Iniciar Servidor")
        self.btn_start.setObjectName("btn_start")
        self.btn_start.clicked.connect(self.start_server)

        self.btn_stop = QPushButton("Stop Server")
        self.btn_stop.setObjectName("btn_stop")
        self.btn_stop.clicked.connect(self.stop_server)
        self.btn_stop.setEnabled(False)

        self.btn_close = QPushButton("Salir")
        self.btn_close.setObjectName("btn_close")
        self.btn_close.clicked.connect(self.close_window)

        layout = QVBoxLayout()
        layout.addWidget(self.text_log)
        layout.addWidget(self.btn_start)
        layout.addWidget(self.btn_stop)
        layout.addWidget(self.btn_close)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.server = Servidor.Server(
            PUERTO,
            SERVER,
            log_callback=self.log_message,
            new_client_callback=self.handle_new_client,
            update_clients=self.handle_new_update_client
        )
        self.server_thread = None
        self.server_broadcast = None

        self.client_windows = []
        self.client_windows_lock = Lock() 
        self.new_client_signal.connect(self.open_window_user)
        self.update_client_signal.connect(self.update_data_User)
        self.log_signal.connect(self.update_log)

    def close_window(self):
        self.close()

    def log_message(self, message):
        self.log_signal.emit(message)

    def closeEvent(self, event):
        confirm = QMessageBox.question(
            self,
            "Cerrar servidor",
            "¿Estás seguro de que deseas cerrar el servidor?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if confirm == QMessageBox.Yes:
            self.stop_server()
            event.accept() 
        else:
            event.ignore()     

    def update_log(self, message):
        self.text_log.append(message)

    def handle_new_client(self, new_user):
        self.new_client_signal.emit(new_user)
    
    def open_window_user(self, user):
        new_window_user = UserWindow(user)
        self.client_windows.append(new_window_user)
        new_window_user.show()
        
    def handle_new_update_client(self, updated_user):
        self.update_client_signal.emit(updated_user)

    def update_data_User(self, user):
        for user_window in self.client_windows:
            if user_window.user.Adrr == user.Adrr:
                user_window.update_user(user)
                if user_window.Disconnect_state:
                        self.client_windows.remove(user_window)
                        self.server.disconnect_user(user.Adrr)      
                elif user_window.user.state:       
                        user_window.close_window()
                        self.client_windows.remove(user_window)
                elif user_window.state_close_process:
                        msg_close_process = user_window.get_process_to_close()
                        self.server.send_menssage_close_process(msg_close_process,user_window.user.Adrr)
                        user_window.state_close_process = False
                     
                        
    def start_server(self):
        if self.server_thread and self.server_thread.is_alive():
            self.log_message("[WARNING] El servidor ya está en ejecución.")
            return
    
        try:
            self.server_thread = threading.Thread(target=self.server.start_server)
            self.server_thread.start()
            self.btn_start.setEnabled(False)
            self.btn_stop.setEnabled(True)
            self.log_message("[STARTING] El servidor está iniciando...")
        except Exception as e:
            self.log_message(f"[ERROR] No se pudo iniciar el servidor: {str(e)}")
            QMessageBox.critical(self, "Error", f"No se pudo iniciar el servidor: {str(e)}")

    def stop_server(self):
        self.server.stop_server()
        if self.server_thread:
            self.server_thread.join()
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.log_message("[SHUTDOWN] El servidor ha sido detenido.")

    def load_stylesheet(self, filename):
        try:
            with open(filename, "r") as file:
                self.setStyleSheet(file.read())
        except FileNotFoundError:
            print(f"No se pudo cargar el archivo {filename}. Verifica la ruta.")    


app = QApplication(sys.argv)
window = Create_Server()
window.show()
sys.exit(app.exec_())