import os
import openpyxl
    
LOGDATA = {}
COMMANDDATA = {}
COMMANDDATA1 = {}

def BDC_Code(integer_input):
    integer_string=str(integer_input)
    int_hex_input= int(integer_string, 16)  # Переводим из 16-ричной в десятичную
    binary_output= bin(int_hex_input)[2:].zfill(len(integer_string.strip())*4)  # на каждую исходную цифру по 4 двоичных
    return(binary_output)

def loaddata():
    try:
        wb = openpyxl.load_workbook('./logdata.xlsx')
    except OSError as err:
        print('ERROR:', err)
    else: 
        ws = wb['DATA']
        if ws == None:
            print('ERROR:', 'sheet none')
        else:
            for row in ws:
                try:

                    databyte=bytearray(13)
                    portkey = str(row[0].value)
                    meterkey = str(row[1].value)
                    
                    databyte[0]= int(row[1].value)                   #MeterAdress
                    databyte[1]= int(BDC_Code(row[6].value),2)      #секунды до
                    databyte[2]= int(BDC_Code(row[5].value),2)      #минуты до
                    databyte[3]= int(BDC_Code(row[4].value),2)      #часы до
                    databyte[4]= int(BDC_Code(row[3].value),2)      #число до
                    databyte[5]= int(BDC_Code(row[2].value),2)      #месяц до
                    databyte[6]= int(BDC_Code(23),2)              #год до
                    databyte[7]= int(BDC_Code(row[9].value),2)     #секунды    после коррекции
                    databyte[8]= int(BDC_Code(row[8].value),2)      #минуты     после коррекции
                    databyte[9]= int(BDC_Code(row[7].value),2)      #часы       после коррекции
                    databyte[10]= int(BDC_Code(row[3].value),2)      #число      после коррекции
                    databyte[11]= int(BDC_Code(row[2].value),2)      #месяц      после коррекции
                    databyte[12]= int(BDC_Code(23),2)              #год        после коррекции
                    if portkey in LOGDATA:
                        if meterkey in LOGDATA[portkey]:
                            RowNo=RowNo+1
                            LOGDATA[portkey][meterkey][RowNo]=databyte
                        else:
                            RowNo=0
                            LOGDATA[portkey][meterkey] = {RowNo: databyte}
                    else:
                        RowNo=0
                        LOGDATA[portkey] = {meterkey:{RowNo: databyte}}
                        
#                    if meterkey == 165:
                except ValueError as err: 
                    print('ERR:', err)
            print('DATA:', LOGDATA)
def GetMeterTimeJornal(socketNo,MeterAdress,RowNo):
    print(socketNo,MeterAdress,RowNo)
    databyte = LOGDATA[str(socketNo)][str(MeterAdress)][RowNo]
    return databyte
def LoadMeterCommand():
    try:
        wb = openpyxl.load_workbook('./logdata.xlsx')
    except OSError as err:
        print('ERROR:', err)
    else: 
        ws = wb['param']
        if ws == None:
            print('ERROR:', 'sheet none')
        else:
            for row in ws:
                databyte=bytearray(20)
                portkey = str(row[0].value)
                meterkey = str(row[1].value)
                command0 = str(row[2].value)
                command1 = str(row[3].value)
                databyte[0]= int(row[1].value)                   #MeterAdress
                for l in range(1,int(row[4].value)+1):
                    databyte[l]= int(row[l+4].value)
                if portkey in COMMANDDATA:
                    if meterkey in COMMANDDATA[portkey]:
                        if command0 in COMMANDDATA[portkey][meterkey]:
                            COMMANDDATA[portkey][meterkey][command0][command1]=databyte[0:int(row[4].value)+1]
                        else:
                            COMMANDDATA[portkey][meterkey][command0] = {command1:databyte[0:int(row[4].value)+1]}
                    else:
                        COMMANDDATA[portkey][meterkey] = {command0:{command1:databyte[0:int(row[4].value)+1]}}
                else:
                    COMMANDDATA[portkey] = {meterkey: {command0:{command1:databyte[0:int(row[4].value)+1]}}}
                    
        print('COMMANDDATA:', COMMANDDATA)
def GetMeterAnswer(socketNo,MeterAdress,command0,command1):
    if(int(command0)==0 or int(command0)==1):
        command1=0
    print("GetFuckMeterAnswer",str(socketNo),str(MeterAdress),str(command0),str(command1))
    databyte = COMMANDDATA[str(socketNo)][str(MeterAdress)][str(command0)][str(command1)]
    print("GetFuckMeterAnswer",databyte)
    return databyte


