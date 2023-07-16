import meter_simulator

meter_simulator.loaddata()
#print(meter_simulator.LOGDATA)
for key, value in meter_simulator.LOGDATA.items():
    for key2, value2 in meter_simulator.LOGDATA[key].items():
        print('DATA:', key, key2)
        for a1 in value2:
            print('----------------', a1)
print(meter_simulator.GetMeterTimeJornal(55011,33,5))
print(meter_simulator.GetMeterTimeJornal(55005,35,5))
