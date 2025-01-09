import psutil
import time

class Recurs:

    def __init__():          
        pass
    
    def get_memory_info():

        cpu_freq = psutil.cpu_freq()

        if cpu_freq:
            velocidad_mhz = cpu_freq.current
            memory = psutil.virtual_memory()
            memory_data = {
                'Total_Memoria': str(round(memory.total / (1024 ** 3),2)) + " Gb",          
                'Memoria_en_uso': str(round(memory.used / (1024 ** 3),2)),             
                'Porcentaje_en_Uso': str(memory.percent) + "%",      
                'Velocidad': str(velocidad_mhz) + " Mhz"
            }
            return memory_data
        else:
            return "Hubo un Error al obtener los datos"        
        
        
    
    def get_cpu_info():
        cpu_data = {
            'Uso_Total_CPU': str((psutil.cpu_percent(interval=1))) + "%",  
            'Velocidad_CPU_GHz': str(psutil.cpu_freq().current / 1000) + " Ghz",    
        }
        
        return cpu_data

    def get_disk_info():
        disk_info = {}
        for disk_name, disk_stats in psutil.disk_io_counters(perdisk=True).items():

            read_start = disk_stats.read_bytes
            write_start = disk_stats.write_bytes
            time.sleep(1) 
        

            disk_stats = psutil.disk_io_counters(perdisk=True)[disk_name]
            read_end = disk_stats.read_bytes
            write_end = disk_stats.write_bytes

            velocidad_lectura = (read_end - read_start) / 1024 
            velocidad_escritura = (write_end - write_start) / 1024  
        
            tiempo_actividad = (read_end + write_end) / 1000  
            tiempo_respuesta = (disk_stats.read_time + disk_stats.write_time) / (disk_stats.read_count + disk_stats.write_count) if disk_stats.read_count + disk_stats.write_count > 0 else 0
        
            disk_info = {
                'Tiempo_Actividad': tiempo_actividad,  
                'Tiempo_Respuesta_ms': tiempo_respuesta,
                'Velocidad_Lectura_KBps': velocidad_lectura, 
                'Velocidad_Escritura_KBps': velocidad_escritura  
            }
    
        return disk_info

    def get_disk_data():
        disk = psutil.disk_usage('/')
        disk_data = {
            'Total_Disco': str(round(disk.total/(1024 ** 3))) + " Gb",          
            'Espacio_Utilizado': str(round(disk.used/(1024 ** 3))),           
        }
        return disk_data

    def get_running_processes():
        processes = []  
        seen_pids = set()  

        for proc in psutil.process_iter(['pid', 'name', 'username', 'status']):
            try:
                if proc.info['status'] in [psutil.STATUS_RUNNING, psutil.STATUS_SLEEPING]:
                    if proc.info['pid'] not in seen_pids:  
                        cpu_percent = proc.cpu_percent(interval=0.1)
                        memory_info = proc.memory_info()
                        process_info = {
                            'PID': proc.info['pid'],
                            'Nombre': proc.info['name'],
                            'CPU (%)': cpu_percent,
                            'Memoria (RSS)': memory_info.rss,  
                            'Memoria (VMS)': memory_info.vms,  
                        }
                    
                        processes.append(process_info)  
                        seen_pids.add(proc.info['pid'])  
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

        return processes

