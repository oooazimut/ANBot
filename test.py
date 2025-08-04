from service.modbus import convert_to_bin


a = convert_to_bin(1, 5)

for x in a:
    print(type(x))
