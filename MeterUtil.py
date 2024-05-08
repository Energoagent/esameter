import datetime
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
def GetSerial(databyte):
    print("getSerial")
    SerialNo=''
    FactoryData=''
    for i in range (len(databyte)):
        print (i, databyte[i])
        if(i<4):
            SerialNo += str(databyte[i]) if databyte[i]>9 else (str(0)+str(databyte[i]))
        else:
            FactoryData+= str(databyte[i]) if databyte[i]>9 else (str(0)+str(databyte[i]))
#    SerialNo = str(databyte[0])+ str(databyte[1])+ str(databyte[2])+ str(databyte[3])
    print("SerialNo=", SerialNo,"FactoryData=",FactoryData)  
    return (SerialNo, FactoryData)

def BDC_Code(integer_input):
    integer_string=str(integer_input)
#    print("integer_string= ",integer_string)
    int_hex_input= int(integer_string, 16)  # Переводим из 16-ричной в десятичную
    binary_output= bin(int_hex_input)[2:].zfill(len(integer_string.strip())*4)  # на каждую исходную цифру по 4 двоичных
#    print("binary_output= ",binary_output, int_hex_input)
    return(binary_output)


def BDC_Decode(data: bytes):
    '''
    Decode BCD number
    '''
    data=data.zfill(8) 
#    print("binary_input= ",data, "type",type(data), len(data))
#    data=reversed(data)
    res = int(data[0:-4],2)*10+int(data[-4:],2)
#    print("data  ",data, data[0:-4],data[-4:])        
#    print("BDC_DECODE  res= ",res )        
    return res


def ParseTimeMeter(data):
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
    return(MeterTime)
#def ReciveDataTimeOut(data, TimeOut):
#    StartTime=current_date_time = datetime.datetime.now()
#    return (data, TimeOutFlag)
