import re

bus_number = re.findall('\d+-?\d+', '1')
print(bus_number)
print(not bus_number)