
class User:

    def __init__(self, Adrr):        
        self.name = None
        self.contraseña = None
        self.menssage = None
        self.state = False
        self.Adrr = Adrr
        self.system_data = {}
        self.procesos = {}
    
    def get_Adrr(self):
        return self.Adrr
    
    def user_relationship(self, data, new_user):
        if isinstance(data, str):
            new_user.set_msg_and_name(data)
        elif isinstance(data, dict):
            new_user.set_system(data)
        elif isinstance(data, list):
            new_user.set_process(data)            
        elif isinstance(data, int):
            new_user.set_msg_and_name(str(data))
        elif isinstance(data, float):
            new_user.set_msg_and_name(str(data))
    
    def set_msg_and_name(self, new_menssage):
        if isinstance(new_menssage, str) and new_menssage != "":
            if self.name == None:        
                self.name = new_menssage
            elif self.contraseña == None:
                self.contraseña = new_menssage
            else:
                self.menssage = new_menssage
        else:
            print("Error: El nombre debe ser una cadena no vacía.")

    def set_adrr(self, new_Adrr):
        if isinstance(new_Adrr, tuple) and new_Adrr != "":
            self.Adrr = new_Adrr
        else:
            print("Error: No IP")            

    def set_system(self, new_system_data):
        if isinstance(new_system_data, dict) and new_system_data != "":
                self.system_data = new_system_data

        else:
            print("Error: No data")            

    def set_process(self, new_list_process):
        if isinstance(new_list_process, list) and new_list_process != "":
                self.procesos = new_list_process

