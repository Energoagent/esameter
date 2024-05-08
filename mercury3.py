import socket
import selectors
import struct
import time
import datetime
import logging
from binascii import hexlify

#Команды счетчика
class MeterCommandCode:
   TEST_CHANNEL      =  1
   SERIAL_NUMBER     =  1
   OPEN_CHANNEL      =  2
   READ_SERIAL_NUM   =  3
   READ_TIME_JOURNAL =  4
   READ_TIME         =  5
   UNKNOWN           =  -1
   
def DefToNow(time):#Разница в мск между заданным временем и текущем
   dt = datetime.datetime.now() - time
   ms = (dt.days * 24 * 60 * 60 + dt.seconds) * 1000 + dt.microseconds / 1000.0
   return ms
def crc16(data):
    crc = 0xFFFF
    for pos in data:
        crc ^= pos 
        for i in range(8):
            if ((crc & 1) != 0):
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
#    return crc
    return bytes([crc % 256, crc >> 8 % 256])
READ=1
NONE=0
class Meter:
    """       команда      статус    функция      """
    
    
    def __init__(self,sn:int,host,port,Process):
        
        self.ReadParam=([[ b'\x04\x00',  0,  self.get_time,datetime.datetime.now()],
                    [ b'\x08\x01',  0,  self.read_param,datetime.datetime.now()],
                    [ b'\x08\x13',  0,  self.read_data,datetime.datetime.now()],     
                   ])
        self.Process=Process #1-ReadMeterParameter, 2-ReadData
        self.CurrentStatus=NONE
        self.ReadTimeOut=10
        self.AttemptNumber=3
        self.sock = socket.socket()
        try:
             self.sock.connect((host,port )) #8686
             self.sock.setblocking(False)
        except ConnectionRefusedError:
            print('ConnectionRefusedError ')
            self.connected=0
            return
        except Exception:
            print('Это что ещё такое? ', Exception)
        finally:        
            self.sn=sn
            self.OpenChannel=0
            self.connected=1
            self.mask=selectors.EVENT_WRITE #готов к записи
            print("Connected ",self.sock)
            self.state=1
        return
    def close(self):
        self.send_to_meter(b'\x02')
        data=self.recive_from_meter()
        print ("Закрытие канала связи", data )
        return self.sock.close()






    def ProcessMeter(self,mask=0):
        print('Process meter ', mask)# Если mask=1, то вошли через обратный вызов, если =0, то новых данных нет
        if mask==0 and self.CurrentStatus==READ: #ожидаем чтение из сокета
            if (DefToNow(self.StartReadTime)/1000>self.ReadTimeOut): #Проверяем, не вышли ли за TimeOut
                #вышли
                print("DefToNow",DefToNow(self.StartReadTime)/1000)
                if self.AttemptNumber<0:  #Кончилось количество повторов, убираем счетчик из опроса
                        print('Конец опроса по кол-ву попыток', self.command, ' CMD ',self.cmd)
#                        self.cmd[1]=0
                else:   #Повтор опроса, умеьшаем количество попыток
                    print('Повтор опроса ', self.AttemptNumber,self.ReadParam)
                    self.AttemptNumber-=self.AttemptNumber
                    self.send_to_meter(self.LastCommand)
        if not self.OpenChannel :
            self.UserLevel=1
            self.open_channel()
        elif self.Process==1 :
            for self.cmd in self.ReadParam:
#Отправка Команды
                if self.cmd[1] == 0: 
                    print('cmd[0] ', self.cmd[0])
                    self.ansver_function=self.cmd[2]                                        
                    self.send_to_meter(self.cmd[0])                    
                    self.cmd[1]=1
                    break
        return


    def chek_meter(self):
#        self.CurrentFunction=self.chek_meter
        print('Chek meter State ', self.state)
        self.ansver_function=self.chek_meter
        match self.state:
            case 1:
                 print("222")
                 self.UserLevel=1   
                 if self.open_channel():
                    self.state=3
            case 3:
                 print("333")
                 if self.get_time():
                    self.state=4
                    print('Test     ')
            case 4:
                 if self.read_param(self.mask):
                    self.state=5
#                    self.sel.register(self.sock, selectors.EVENT_READ, self.ansver_function)  
            case 5:
                 self.close()
                 self.state=0                 
            case _:
                pass
        print('State_1', self.state)
        return
    def read_data(self):
        print("read data Last Interval")        
        if self.mask==selectors.EVENT_WRITE:
            self.ansver_function=self.read_data
#            MyMeter.read_data('\x08\x13')
            print ("Запрос профиля средних мощностей", data)            
            return 0
        elif self.mask==selectors.EVENT_READ:
            data=""
            data=self.recive_from_meter()
            data=str(hexlify(data),"utf-8")
            print ("Запрос последней записи", data,"    ")
            #FactoryNo=int(str(data[1:2]))*10+int(str(data[15]))+2000
            self.LastRecordAdr=data[2:6]#+str(int(data[4:6],base=16))+str(int(data[6:8],base=16))+str(int(data[8:10],base=16))
            self.StatusByte=data[6:8]
            self.LastRecordData=data[8:10]+"."+data[10:12]+" "+data[12:14]+"."+data[14:16]+"."+data[16:18]
#            self.SoftVersion=str(int(data[16:18],base=16))+"."+str(int(data[18:20],base=16))+"."+str(int(data[20:22],base=16))
            print ("LastRecordAdr= ",self.LastRecordAdr, "self.StatusByte ",self.StatusByte,"self.LastRecordData ",self.LastRecordData)#, "Версия ПО ",self.SoftVersion)        
            return True    
    def read_param(self):
        print("read param ", self.mask )        
        if self.mask==selectors.EVENT_WRITE:
            self.ansver_function=self.read_param
            MyMeter.send_to_meter(b'\x08\x01')
            print ("Запрос паспортных характеристик", data)            
            return 0
        elif self.mask==selectors.EVENT_READ:
            data=""
            data=self.recive_from_meter()
            data=str(hexlify(data),"utf-8")
            print ("Чтение паспортных характеристик", data,"    ")
            #FactoryNo=int(str(data[1:2]))*10+int(str(data[15]))+2000
            self.FactoryNo=str(int(data[2:4],base=16))+str(int(data[4:6],base=16))+str(int(data[6:8],base=16))+str(int(data[8:10],base=16))
            self.FactoryData=str(int(data[10:12],base=16))+"."+str(int(data[12:14],base=16))+"."+str(int(data[14:16],base=16))
            self.SoftVersion=str(int(data[16:18],base=16))+"."+str(int(data[18:20],base=16))+"."+str(int(data[20:22],base=16))
            print ("Заводской номер ",self.FactoryNo, "Data Изготовления ",self.FactoryData, "Версия ПО ",self.SoftVersion)        
            return True
    def get_time(self):
        print("get time ", self.mask )
        if self.mask==selectors.EVENT_WRITE:
            self.ansver_function=self.get_time
 #           self.send_to_meter(b'\x04\x00')
            print("get time отправка команды " )
            return 0
        elif self.mask==selectors.EVENT_READ:
            data=self.recive_from_meter()
            data=str(hexlify(data), "utf-8")
            print ("Запрос времени, чтение", data)
            year=int(str(data[14]))*10+int(str(data[15]))+2000
            month=int(str(data[12]))*10+int(str(data[13]))
            day=int(str(data[10]))*10+int(str(data[11]))
            hour=int(str(data[6]))*10+int(str(data[7]))
            minute=int(str(data[4]))*10+int(str(data[5]))
            second=int(str(data[2]))*10+int(str(data[3]))
            print("Time " ,year, month, day, hour, minute, second)
            now = datetime.datetime.now()
            MeterTime = datetime.datetime(year, month, day, hour, minute, second)
            timedelta=now-MeterTime
            print("Timedelta", timedelta,now,MeterTime)
            return True
    def open_channel(self):
        if self.OpenChannel :
            print('Канал уже открыт', self.UserLevel, self.mask )
            return True
        print('Открываем канал', self.UserLevel, self.mask)
        if self.mask==selectors.EVENT_WRITE:
            self.ansver_function=self.open_channel
            if self.UserLevel==1:
                self.send_to_meter(b'\x01\x01\x01\x01\x01\x01\x01\x01')
            elif self.UserLevel==2:
                self.send_to_meter(b'\x01\x01\x02\x02\x02\x02\x02\x02')
            else :
                return 0
        elif self.mask==selectors.EVENT_READ:
            data=self.recive_from_meter()
            print ("Rанал связи открыт", data )
            self.OpenChannel=1
            return True
    def recive_from_meter(self):
        try:
            data = self.sock.recv(1024)
        except BlokingIOError:
            print('recive_from_meter BlokingIOError ')
        except Exception:
            print('Это что ещё такое? ', Exception)
        else:        
            crc=crc16(data)
            self.CurrentStatus=NONE
            self.mask=selectors.EVENT_WRITE  # готов к записи
            self.sel.unregister(self.sock)   
            if int(str(hexlify(crc), "utf-8"))==0:
                print ('recive ', str(hexlify(data), "utf-8"),"CRC OK",crc)
            else:
                print ('recive ', str(hexlify(data), "utf-8"),"CRC BAD",crc)
                data=''
        return data
    def send_to_meter(self,data):
        try:
             self.sel.unregister(self.sock)
        except KeyError:
            print('Not Register ')
        except Exception:
            print('Это что ещё такое? ', Exception)
        finally:
            data = self.sn.to_bytes(1,byteorder='big', signed=False)+data
            data += crc16(data)
            print ('send ', str(hexlify(data), "utf-8"))
            self.LastCommand=data
            self.sock.send(data)
            self.sel.register(self.sock, selectors.EVENT_READ, self.ansver_function)
            self.mask=selectors.EVENT_READ                  #читаем
            self.StartReadTime=datetime.datetime.now()
            self.CurrentStatus=READ
        return 
def MeterRequestType(databyte):
   if((databyte[1]==8) & (databyte[2]==0)):#Читаем  заводской номер счетчика и дату изготовления
      logging.debug("Читаем  заводской номер счетчика и дату изготовления! Адрес счетчика =",databyte[0])      
      return MeterCommandCode.READ_SERIAL_NUM
   elif(databyte[1]==0):#Тест канала связи
      logging.debug("Тест канала связи! Адрес счетчика = {address}".format(address=databyte[0]))            
      return MeterCommandCode.TEST_CHANNEL      
   elif(databyte[1]==1):#Открытие канала связи
      logging.debug("Открытие канала связи! Адрес счетчика ={address}".format(address=databyte[0]))            
      return MeterCommandCode.OPEN_CHANNEL
   elif((databyte[1]==4) & (databyte[2]==2)):#Читаем журнал времени
      logging.debug("Читаем журнал времени!!!!!! Адрес счетчика ={address}".format(address=databyte[0]))
      return MeterCommandCode.READ_TIME_JOURNAL
   elif((databyte[1]==4) & (databyte[2]==0)):
      logging.debug("Читаем время счетчика!!!!!! Адрес счетчика ={address}".format(address=databyte[0]))
      return MeterCommandCode.READ_TIME      
   else:
      logging.debug("Команда не распознана! Адрес счетчика ={address}".format(address=databyte[0]))            
      return MeterCommandCode.UNKNOWN
   
#data=MyMeter.recive_from_meter()
#data=str(hexlify(data), "utf-8")




#MyMeter.close()
