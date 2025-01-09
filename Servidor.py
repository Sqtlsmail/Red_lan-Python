import socket
import threading
import queue
import json  
import User
import time
import gc
import zlib

class Server:
    HEADER = 64
    FORMAT = "utf-8"
    DISCONNECT_MESSAGE = "!DISCONNECT" 

    def __init__(self,PORT,SERVER, log_callback=None, new_client_callback=None, update_clients= None):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.PORT = PORT
        self.SERVER = SERVER #socket.gethostbyname(socket.gethostname())
        self.ADDR = (SERVER, PORT)
        self.server.bind(self.ADDR)
        self.user_dict = {}
        self.server_running = False  
        self.connections = []  
        self.message_queue = queue.Queue() 
        self.log_callback = log_callback  
        self.new_client_callback = new_client_callback 
        self.update_clients = update_clients 
        self.last_list_connect_user = []
        
    def log(self, message):
        if self.log_callback:
            self.log_callback(message)       


    def user_identific(self, addr):
        if addr in self.user_dict:
            return self.user_dict[addr]  
        else:
            new_user = User.User(addr)
            self.user_dict[addr] = new_user
            if self.new_client_callback:
                self.new_client_callback(new_user)
            return new_user

    def user_exist(self, addr, data, connected):
        usuario = self.user_identific(addr)  
        if usuario:
            usuario.user_relationship(data, usuario)
            if data == self.DISCONNECT_MESSAGE:
                usuario.state = True
                self.log(f"[NOTIFICACION] Usuario: {usuario.Adrr} Desconnectado!")
                del self.user_dict[addr]  
                connected = False
            if self.update_clients:
                self.update_clients(usuario)
            self.message_everybody(usuario)
            self.send_list_connect()
        return connected

    def disconnect_user(self, addr):
            usuario = self.user_dict[addr]
            self.msg_one_client(usuario,addr,self.DISCONNECT_MESSAGE)


    def send_menssage_close_process(self, proceso, addr):  
        usuario = self.user_dict[addr]
        message = f"%#!{proceso}"
        self.msg_one_client(usuario,addr,message)

    def msg_one_client(self,usuario,addr,message):
            try:
                message_encoded = json.dumps(message).encode(self.FORMAT)
                message_length = len(message_encoded)
                send_length = str(message_length).ljust(self.HEADER).encode(self.FORMAT)
                for conn in self.connections:
                    if conn.getpeername() == addr:  
                        conn.send(send_length)
                        conn.send(message_encoded)
                        break
            except (BrokenPipeError, OSError):
                self.log(f"[ERROR] Fallo al enviar mensaje a {usuario.name} ({addr[0]})")    

    def message_everybody(self, usuario):
        if usuario.menssage is not None:
            if isinstance(usuario.menssage, str):
                self.message_queue.put(f"{usuario.name}({usuario.Adrr[0]}): {usuario.menssage}")
                usuario.menssage = None
    
    def handle_client(self, conn, addr):
        self.log(f"[NEW CONNECTION] {addr} connected.")
        connected = True
        self.connections.append(conn)  
        self.user_identific(addr)

        while connected and self.server_running:
            time.sleep(0.05)
            try:
                msg_length = conn.recv(self.HEADER).decode(self.FORMAT).strip()
                if msg_length and msg_length.isdigit():
                    msg_length = int(msg_length)
                    compressed_msg = conn.recv(msg_length)
                    try:
                        decompressed_msg = zlib.decompress(compressed_msg).decode(self.FORMAT)
                        data = json.loads(decompressed_msg)
                        if not self.user_exist(addr, data, connected):
                            break
                    except zlib.error:
                        self.log(f"[ERROR] Failed to decompress message from {addr}")
                    except json.JSONDecodeError:
                        self.log(f"[ERROR] Could not decode JSON message from {addr}")


            except (ConnectionResetError, OSError):
                self.log(f"Connection with {addr} was reset or closed.")
                connected = False
                break

        conn.close()
        if conn in self.connections:
            self.connections.remove(conn)
        gc.collect()

    def broadcast_message(self):
        while self.server_running:
            time.sleep(0.5)
            try:
                message = self.message_queue.get(timeout=1)
                message_encoded = json.dumps(message).encode(self.FORMAT)
                message_length = len(message_encoded)
                send_length = str(message_length).ljust(self.HEADER).encode(self.FORMAT)
                for conn in self.connections:
                    try:
                        conn.send(send_length)
                        conn.send(message_encoded)
                    except (BrokenPipeError, OSError):
                        break
            except queue.Empty:
                continue  

    def send_list_connect(self):
        list_connect_user = []
        for obj in self.user_dict.values():
            if obj.name is not None:
                connect_user = f"{obj.name} {obj.Adrr} \U0001F7E2"
                list_connect_user.append(connect_user)
        if list_connect_user != self.last_list_connect_user:
            self.message_queue.put(list_connect_user)
            self.last_list_connect_user = list_connect_user

    def start_server(self):
        if self.server is None or self.server.fileno() == -1:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind(self.ADDR)
        self.server.listen()
        self.log(f"[LISTENING] Servidor escuchando en {self.SERVER}:{self.PORT}")
        self.server_running = True

        self.server_broadcast = threading.Thread(target=self.broadcast_message)
        self.server_broadcast.start()
        self.start_gc()

        while self.server_running:
            try:
                conn, addr = self.server.accept()
                thread = threading.Thread(target=self.handle_client, args=(conn, addr))
                thread.start()
                self.log(f"[ACTIVE CONNECTIONS] {threading.active_count() - 3}")
            except OSError:
                break

    def start_gc(self, interval=60):
        def gc_loop():
            while self.server_running:
                gc.collect()
                time.sleep(interval)

        thread = threading.Thread(target=gc_loop, daemon=True)
        thread.start()

    def stop_server(self):
        self.server_running = False
        if self.server:
            try:
                self.server.close()
            except OSError:
                pass
        self.server = None 
        





