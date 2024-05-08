import select
import errno
import socket
import argparse
import sys
import time
import logging
from MeterUtil import crc16, BDC_Decode, GetSerial
from MeterJornal import FuckMeterTime 
from meter_simulator import loaddata,LoadMeterCommand,GetMeterAnswer,GetMeterTimeJornal


def createParser ():
    parser = argparse.ArgumentParser()
    parser.add_argument ('-cl', nargs='?', default='55008')
    parser.add_argument ('-serv', nargs='?', default='50008')
    return parser
class Meter:
    INPUTS = list()
    OUTPUTS = list()
#        def __init__(self, server_adress,port):
#            print("Создание объекта Meter")
#        def send_to_meter(self, data : b''):
#            print("Hello")
#        def recive_from_meter(self, data : b''):
#            print("Hello")    
#ERVER_ADDRESS = ('192.168.22.21', 8686)
socketNo=55023
ServerPort=8686
# Говорит о том, сколько дескрипторов единовременно могут быть открыты
MAX_CONNECTIONS = 10

# Откуда и куда записывать информацию
INPUTS = list()
OUTPUTS = list()

def get_non_blocking_server_socket():

    # Создаем сокет, который работает без блокирования основного потока
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setblocking(0)

    # Биндим сервер на нужный адрес и порт
    server.bind(('127.0.0.1', ServerPort))

    # Установка максимального количество подключений
    server.listen(MAX_CONNECTIONS)

    return server


def handle_readables(readables, server, clientSock):
    """
    Обработка появления событий на входах
    """
  #  int sn,secBef,minBef,hourBef, Day,Month,Year 
    for resource in readables:

        # Если событие исходит от серверного сокета, то мы получаем новое подключение
        if resource is server:
            connection, client_address = resource.accept()
            print("resource is server 1: ", resource)            
            connection.setblocking(0)
            INPUTS.append(connection)
            logging.debug("new connection from {address}".format(address=client_address))

        # Если событие исходит не от серверного сокета, но сработало прерывание на наполнение входного буффера
        else:
            data = ""
            try:
                data = resource.recv(1024)
            # Если сокет был закрыт на другой стороне
            except ConnectionResetError:
                pass

            if data:
                databyte=bytearray(data)
                print("Getting databyte ",databyte)
                for i in range(len(databyte)-2):
                    print("get ",i,databyte[i])
                if((databyte[1]==4) & (databyte[2]==2)):
                    print("Меняем журнал времени!!!!!! Адрес счетчика =",databyte[0],"SocketNo",socketNo)
                    databyte=GetMeterTimeJornal(socketNo,databyte[0],databyte[3])
                    crc = crc16(databyte)
                    data=databyte+crc
                    databyte=bytearray(data)
#                    print("read Answer: {data}".format(data=str(data)))
                    resource.send(data)
                    logging.debug("Ответили клиенту")                            
#                    else:
#                        clientSock.send(databyte) #пересылаем запрос дальше, на счетчик
#                        data=clientSock.recv(1024)
                elif((databyte[1]==4) & (databyte[2]==0)):
                    print("Читаем  время!!!!! Адрес счетчика =",databyte[0],"SocketNo",socketNo)
#                    clientSock.send(databyte) #пересылаем запрос дальше, на счетчик
#                    data=clientSock.recv(1024)
#                    print("Время= ",data)
                    TimeDatabyte=bytearray(data)
#                    for i in range(len(TimeDatabyte)):
#                        print("Time [i] ",i,BDC_Decode(bin(TimeDatabyte[i])[2:]))                      
                    databyte=FuckMeterTime(databyte[0] )
                    print("Время заменили",databyte[0])
                    for i in range(len(databyte)):
                        print("FuckTime [i] ",i,BDC_Decode(bin(databyte[i])[2:]))                    
                    crc = crc16(databyte)
                    data=databyte+crc
                    resource.send(data)
                    logging.debug("Ответили клиенту")                       
                    print("Время= ",data)
                else:
#                    print("пересылаем запрос дальше, на счетчик",databyte)                        
#                    clientSock.send(databyte) #пересылаем запрос дальше, на счетчик                       
#                    data=clientSock.recv(1024)
#                    rsvdatabyte=bytearray(data)
#                    crc = crc16(rsvdatabyte)
#                    print("crc= ",crc)
#                    print("Прочитали ответ счетчика ",rsvdatabyte)                    
#                    for i in range(len(rsvdatabyte)-2):
#                        print("ans meter",i,rsvdatabyte[i])
                    databyte=GetMeterAnswer(socketNo,databyte[0],databyte[1],databyte[2])
                    print("Прочитали fuck счетчика из Excel",databyte)                    
                    for i in range(len(databyte)):
                        print("fuck ",i,databyte[i])
                    crc = crc16(databyte)
                    data=databyte+crc
                    databyte=bytearray(data)
                    resource.send(databyte)                
                    print("Ответили клиенту ",databyte)
                    for i in range(len(databyte)-2):
                        print("send ",i,databyte[i])
#                        combiner = "".join(fragments)
#                        print("combiner ",combiner)
#                        data=clientSock.recv(1024)
          
 #               Ask=""                                
                # Говорим о том, что мы будем еще и писать в данный сокет
 #               if resource not in OUTPUTS:
 #                   OUTPUTS.append(resource)

            # Если данных нет, но событие сработало, то ОС нам отправляет флаг о полном прочтении ресурса и его закрытии
            else:

                # Очищаем данные о ресурсе и закрываем дескриптор
                clear_resource(resource)


def clear_resource(resource):
    """
    Метод очистки ресурсов использования сокета
    """
    if resource in OUTPUTS:
        OUTPUTS.remove(resource)
    if resource in INPUTS:
        INPUTS.remove(resource)
    resource.close()

    print('closing connection ' + str(resource))


def handle_writables(writables, Ask, Answer):

    # Данное событие возникает когда в буффере на запись освобождается место
    for resource in writables:
        try:
            if Answer:
                resource.send(Answer)
                print("sendinging data: {Answer}")
                Answer=""
#               resource.send(bytes('Hello from server!', encoding='UTF-8'))
        except OSError:
            clear_resource(resource)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    parser = createParser()
    namespace = parser.parse_args (sys.argv[1:])
    print (namespace)
#    print ("Socket {}!".format (namespace.p) )
    socketNo=namespace.cl
    ServerPort=int(namespace.serv)

    # Создаем серверный сокет без блокирования основного потока в ожидании подключения
    server_socket = get_non_blocking_server_socket()
    INPUTS.append(server_socket)
    print("Server socket", server_socket)
    # Создаем клиентский сокет
    Clientsock = socket.socket()
    Clientsock.connect(('192.168.22.21',int(socketNo) ))
    print("connect to socket", socketNo)
    loaddata()
    LoadMeterCommand()

    print("server is running, please, press ctrl+c to stop")

    
    try:
        while INPUTS:
            readables, writables, exceptional = select.select(INPUTS, OUTPUTS, INPUTS)
            handle_readables(readables, server_socket, Clientsock)
#            handle_writables(writables, Ask, Answer)              
    except KeyboardInterrupt:
        clear_resource(server_socket)
        print("Server stopped! Thank you for using! SocketNo",socketNo )
