import os
import openpyxl
    
LOGDATA = {}

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
                            LOGDATA[portkey][meterkey].append(databyte)
                        else:
                            LOGDATA[portkey] = {meterkey: [databyte]}
                    else:
                        LOGDATA[portkey] = {meterkey: [databyte]}
                except ValueError: pass

def GetMeterTimeJornal(socketNo,MeterAdress,RowNo):
    databyte = LOGDATA[str(socketNo)][str(MeterAdress)][RowNo]
    return databyte

