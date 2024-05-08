import time
from MeterUtil import BDC_Code

def FuckMeterTime(MeterAdress ):
#    time.sleep(1)
    databyte=bytearray(9)
    databyte[0]= MeterAdress
    
    databyte[1]= int(BDC_Code(time.strftime('%S')),2)  #секунды 35
    databyte[2]= int(BDC_Code(time.strftime('%M')),2)  #минуты 59
    databyte[3]= int(BDC_Code(time.strftime('%H')),2)  #часы 13
    databyte[4]= int(BDC_Code(time.strftime('%w')),2)  #номер дня недели    
    databyte[5]= int(BDC_Code(time.strftime('%d')),2)  #число
    databyte[6]= int(BDC_Code(time.strftime('%m')),2)  #месяц
    databyte[7]= int(BDC_Code(time.strftime('%y')),2)  #год
    databyte[8]= int(BDC_Code(1),2)                    #зимнее
    return(databyte)
   





