########################################################################################################
#                                           STM CONNECTION MODULE                                      #
# El objetivo es realizar más fácilmente la tarea de conexión y recolección de datos de la placa STM32 #
#                                   Autor: Antonio Carretero Sahuquillo                                #
########################################################################################################

# Librerías #
import serial.tools.list_ports 
import numpy as np
import threading

#FUNCIÓN DEL PROGRAMA#
def lab3_calc(ser, show, vref, rref):
    #Cáclulo voltaje del ADC
    voltaje = (ser.data/4095) * 3.3

    #Cálculo de la resistencia
    resistencia = (-voltaje * rref)/(voltaje - vref)

    #Cálculo de la temperatura por la aproximación Steinhart-hart
    a_coef = [0.00106351, 0.00018395, 1.13543794e-07] 
    temperatura = 1/(a_coef[0] + a_coef[1]*np.log(resistencia) + a_coef[2]*np.log(resistencia)**3)       

    if show == True:
        print("Voltaje: ", voltaje)
        print("Resistencia: ", resistencia)
        print("Temperatura: ", (temperatura-273.15)) 


# Clase #  -- Instancia de la conexión
class stm_conn(serial.Serial):
    ###############
    ## ATRIBUTOS ##
    portName = " "   # Nombre del puerto
    
    reading = False     # Leer?
    data = 0            # Datos
    newData = False     # Indica si se ha leído un dato
    dataShow = False    # Mostrar por consola?

    #################
    ## CONSTRUCTOR ##
    def __init__(self, show):
        super().__init__()
        self.dataShow = show
        self.baudrate = 115200  #Por defecto, al crear la instancia se asigna dicho valor de baudrate

    ########################
    ## MÉTODOS "PÚBLICOS" ##
    """
    @brief Selecciona el puerto donde se realiza la comunicación con la placa
    @param None
    @retval None
    """
    def select_port(self):
        portList = self.__get_portList()
        portVal = input("Selecciona número de puerto (Windows): COM")
        self.portName = self.__check_port(portList, portVal)

    """
    @brief Lee (o para de leer) datos del búfer de entrada, en tiempo real
    @param None
    @retval None
    """
    def rtRead_data_start(self):
        self.rth = threading.Thread(target=self.__read_thread, daemon=True, args=(self.dataShow,))
        self.reading = True
        self.rth.start()
        
    def rtRead_data_stop(self):
        self.reading = False
        self.rth = 0

    """
    @brief Apertura y cierre de la conexión en el puerto seleccionado
    @param None
    @retval None
    """
    def open_conn(self):
        if self.portName != " ":
            self.port = self.portName
            self.open()

    def close_conn(self):
        self.close()

    """
    @brief Lectura controlada de los datos leídos en el hilo
    @param None
    @retval None
    """
    def get_newData(self):
        if self.newData:
            return self.data
        else:
            return -1



    ########################
    ## MÉTODOS "PRIVADOS" ##
    
    """
    @brief Muestra la lista de puertos disponibles por pantalla y devuelve una lista con dichos puertos
    @param None
    @retval None
    """
    def __get_portList(self):
        ports = serial.tools.list_ports.comports()
        portList = []

        print("\n", "LISTA DE PUERTOS: \n")
        for onePort in ports:                           
            portList.append(str(onePort))
            print(str(onePort)) 
        
        print("\n")
        return portList

    """
    @brief Comprueba si el puerto introducido está en la lista y devuelve su nombre
    @param None
    @retval None
    """
    def __check_port(self, portList, portVal):
        for x in range(0, len(portList)):               
            if portList[x].startswith("COM" + str(portVal)):
                portVal = "COM" + str(portVal)             
                print("Puerto seleccionado: ", portList[x], "\n")
                return portVal
        
        print("[STM_CONN-ERR]: El puerto seleccionado no está disponible")
        return 0

    """
    @brief Hilo de ejecución para la lectura en "paralelo" de los datos de entrada
    @param None
    @retval None
    """         
    def __read_thread(self, show):
        while self.reading:
            count = self.in_waiting
            if count > 0:
                #Lectura del código ADC
                self.data = int.from_bytes(self.read(2), byteorder="little", signed=False)
                self.newData = True

                if show == True:
                    print("\n DATOS:")
                    print("Código: ", str(self.data))  

                ## FUNCION PARA EL LABORATORIO ##
                lab3_calc(self, show, 3.3, 500000)  
