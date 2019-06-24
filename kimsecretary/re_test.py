import re
import requests
from bs4 import BeautifulSoup as BS

p = re.compile(r'\d+[-]\d+')
# m = p.search('88번')
num = '3007번'
m = re.findall('\d+-?\d+', num)[0]
print(m)

url = 'http://openapi.gbis.go.kr/ws/rest/busrouteservice?serviceKey=p7RiOnONfT8hc4MMVfKU8%2BSr2pQ8vwgM3JQA0sap60em7nJZW5QpGUrGcDmQy4nqe%2B1YxAOAwL7F1uRrlk8PkQ%3D%3D&keyword=3100'
request = requests.get(url).text
soup = BS(request, 'html.parser')
bus_list = soup.find('msgbody')

routeid_list = []
print('버스를 선택하세요. ex) 1, 1번')
for idx, bus in enumerate(bus_list):
    print(idx+1)
    print('운행지역:'+bus.find('regionname').contents[0])
    print('버스번호:'+bus.find('routename').contents[0])
    print('버스종류:'+bus.find('routetypename').contents[0])
    routeid_list.append(bus.find('routeid').contents[0])

user_input = 2
# bus = bus_list[1]
print(routeid_list[2-1])

# print(result)
