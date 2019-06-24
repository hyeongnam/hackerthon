import requests
from bs4 import BeautifulSoup as BS


url = 'http://openapi.gbis.go.kr/ws/rest/busarrivalservice?serviceKey=p7RiOnONfT8hc4MMVfKU8%2BSr2pQ8vwgM3JQA0sap60em7nJZW5QpGUrGcDmQy4nqe%2B1YxAOAwL7F1uRrlk8PkQ%3D%3D&stationId=121000921&routeId=200000110&staOrder=39'
request = requests.get(url).text
soup = BS(request, 'html.parser')
# 되기는 하지만 너무 길다..
# test = soup.select_one('response > msgBody > busArrivalItem > locationNo1').contents[0]

predict1 = soup.find('predicttime1').contents[0]
location1 = soup.find('locationno1').contents[0]
seat1 = soup.find('remainseatcnt1').contents[0]

predict2 = soup.find('predicttime2').contents[0]
location2 = soup.find('locationno2').contents[0]
seat2 = soup.find('remainseatcnt2').contents[0]




