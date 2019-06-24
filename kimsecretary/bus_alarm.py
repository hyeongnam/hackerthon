from decouple import config
import requests
import sys
from bs4 import BeautifulSoup as BS
import os

chat_id = sys.argv[1]
minute = sys.argv[2]

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

token = config('TOKEN')
api_url = f'https://api.telegram.org/bot{token}'

if int(predict1) <= int(minute):

    msg = f'직전 버스 {predict1}분 ({location1}정류장) [{seat1}좌석]\n' \
        f'다음 버스 {predict2}분 ({location2}정류장) [{seat2}좌석]\n' \
        f'1분 간격으로 알려드리며 종료, 정지 등으로 종료할 수 있습니다.'
    requests.get(api_url + f'/sendMessage?chat_id={chat_id}&text={msg}')


else:
    msg=f'else.. predict={predict1}, minute={minute}'
    requests.get(api_url + f'/sendMessage?chat_id={chat_id}&text={msg}')
