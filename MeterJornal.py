def BDC_Code(integer_input):
    integer_string=str(integer_input)
    print("integer_string= ",integer_string)
    int_hex_input= int(integer_string, 16)  # Переводим из 16-ричной в десятичную
    binary_output= bin(int_hex_input)[2:].zfill(len(integer_string.strip())*4)  # на каждую исходную цифру по 4 двоичных
    print("binary_output= ",binary_output)
    return(binary_output)
def BDC_Decode(binary_input):
    n = int(binary_input, 2)
    integer_output = n.to_bytes((n.bit_length() + 7) // 8, 'big').decode()
    return(integer_output)  
def GetMeterTimeJornal(socketNo,MeterAdress,RowNo):
#    print("+StringChanged+ ",socketNo, " sn ", MeterAdress, " RowNo ", RowNo   )
    if((socketNo==55005) & (MeterAdress ==35) & (RowNo==5)):
        databyte=bytearray(13)
        databyte[0]= MeterAdress
        databyte[1]= int(BDC_Code(35),2)  #секунды 35
        databyte[2]= int(BDC_Code(59),2)  #минуты 59
        databyte[3]= int(BDC_Code(13),2)  #часы 13
        databyte[4]= int(BDC_Code(11),2)  #число
        databyte[5]= int(BDC_Code(1),2)   #месяц
        databyte[6]= int(BDC_Code(23),2)  #год
        databyte[7]= int(BDC_Code(38),2)  #секунды    после коррекции
        databyte[8]= int(BDC_Code(59),2)  #минуты     после коррекции
        databyte[9]= int(BDC_Code(13),2)  #часы       после коррекции
        databyte[10]= int(BDC_Code(11),2) #число      после коррекции
        databyte[11]= int(BDC_Code(1),2)  #месяц      после коррекции
        databyte[12]= int(BDC_Code(23),2) #год        после коррекции
#        print("+++++++++++StringChanged+++++")
#        print(databyte)
    if((socketNo==55005) & (MeterAdress ==35) & (RowNo==7)):
        databyte=bytearray(13)
        databyte[0]= MeterAdress
        databyte[1]= int(BDC_Code(35),2)  #секунды 35
        databyte[2]= int(BDC_Code(59),2)  #минуты 59
        databyte[3]= int(BDC_Code(13),2)  #часы 13
        databyte[4]= int(BDC_Code(11),2)  #число
        databyte[5]= int(BDC_Code(1),2)   #месяц
        databyte[6]= int(BDC_Code(23),2)  #год
        databyte[7]= int(BDC_Code(38),2)  #секунды    после коррекции
        databyte[8]= int(BDC_Code(59),2)  #минуты     после коррекции
        databyte[9]= int(BDC_Code(13),2)  #часы       после коррекции
        databyte[10]= int(BDC_Code(11),2) #число      после коррекции
        databyte[11]= int(BDC_Code(1),2)  #месяц      после коррекции
        databyte[12]= int(BDC_Code(23),2) #год        после коррекции
        print("+++++++++++StringChanged+++++")
        print(databyte)
    return(databyte)


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
