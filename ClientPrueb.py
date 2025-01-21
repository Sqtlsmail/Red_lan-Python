
import socket
import threading
import json
import time
import zlib
import psutil

from PyQt5.QtCore import QObject,pyqtSignal
import classRecolect


class Client(QObject):
    message_received = pyqtSignal(str)
    list_connect_recived = pyqtSignal(list)

    def __init__(self,SERVER,PUERTO, usuario, contraseña):
        super().__init__()
        self.usuario = usuario
        self.contraseña = contraseña
        self.HEADER = 64
        self.PORT = PUERTO
        self.SERVER = SERVER        
        self.FORMAT = "utf-8"
        self.DISCONNECT_MESSAGE = "!DISCONNECT"
        self.ADDR = (self.SERVER, self.PORT)
        self.connected = True
        self.Recolector = classRecolect.Recurs

    def new_system(self):
        memory_data = self.Recolector.get_memory_info()
        cpu_data = self.Recolector.get_cpu_info()
        disk_info = self.Recolector.get_disk_info()
        disk_data = self.Recolector.get_disk_data()
        system_data = {
            'memory': memory_data,
            'cpu': cpu_data,
            'disk_info': disk_info,
            'disk_data': disk_data
        }
        return system_data

    def send_system(self, client):
        while self.connected:
            try:
                system_data = self.new_system()
                if isinstance(system_data, dict) and system_data:
                    self.send(system_data, client)
                time.sleep(5)
            except OSError as e:
                print(f"[ERROR] Error al enviar datos del sistema: {e}")
                self.connected = False
                break

    def send_procesos(self, client):
        while self.connected:
            try:
                running_processes = self.Recolector.get_running_processes()
                processes_data = []  

                for process in running_processes:
                    process_data = {
                        "PID": process["PID"],
                        "Nombre": process["Nombre"],
                        "CPU (%)": process["CPU (%)"],
                        "Memoria RSS (MB)": process["Memoria (RSS)"] / (1024**2),
                        "Memoria VMS (MB)": process["Memoria (VMS)"] / (1024**2),
                    }
                    processes_data.append(process_data)  

                self.send(processes_data, client)
                time.sleep(5)

            except OSError as e:
                print(f"[ERROR] Error al enviar datos de procesos: {e}")
                self.connected = False
            break



    def decifrar_mensaje(self, mgs_cifrar_process):
        if not isinstance(mgs_cifrar_process, str) or not mgs_cifrar_process.strip():
            return None
        mgs_cifrar_process = mgs_cifrar_process.strip()
        prefix = "%#!"
        if mgs_cifrar_process.startswith(prefix):
            return mgs_cifrar_process[len(prefix):]  
    
        return None


    def receive(self, client):
        while self.connected:
            try:
                msg_length = client.recv(self.HEADER).decode(self.FORMAT).strip()
                if msg_length and msg_length.isdigit():
                    msg_length = int(msg_length)
                    msg = client.recv(msg_length).decode(self.FORMAT)
                    try:
                        data = json.loads(msg)
                        if isinstance(data, list):  # Si los datos son una lista
                            self.list_connect_recived.emit(data)  # Convertir a JSON
                        elif isinstance(data, str):
                            msg_close_process = self.decifrar_mensaje(data)
                            if msg_close_process != None:
                                self.finalizar_proceso_por_nombre(msg_close_process)
                            else:
                                self.message_received.emit(data)
                    except json.JSONDecodeError:
                        self.message_received.emit(msg)
            except Exception as e:
                self.message_received.emit(f"[ERROR]: {e}")
                self.connected = False
                break

    def send(self, msg, client):
        try:
            message = json.dumps(msg).encode(self.FORMAT)
            compressed_message = zlib.compress(message)  
            
            msg_length = len(compressed_message)
            if msg_length == 0:
                return
            send_length = str(msg_length).encode(self.FORMAT)
            send_length += b" " * (self.HEADER - len(send_length))
            client.send(send_length)
            client.send(compressed_message)
        except Exception as e:
            self.connected = False

    def start(self):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client.connect(self.ADDR)
            self.send(self.usuario, client)
            self.send(self.contraseña, client)

            receive_thread = threading.Thread(target=self.receive, args=(client,))
            data_system = threading.Thread(target=self.send_system, args=(client,))
            data_process = threading.Thread(target=self.send_procesos, args=(client,))
            data_system.daemon = True
            data_process.daemon = True
            receive_thread.daemon = True
            receive_thread.start()
            data_system.start()
            data_process.start()            

            return client

        except Exception as e:
            self.connected = False
            return None

    def finalizar_proceso_por_nombre(self,proceso):
        procesos_terminados = 0
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'].lower() == proceso.lower():  
                try:
                    proc.kill()  
                    procesos_terminados += 1
                    return
                except psutil.NoSuchProcess:
                    return
                except psutil.AccessDenied:
                    return
        if procesos_terminados == 0:
            return
        




