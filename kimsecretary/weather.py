import requests
from bs4 import BeautifulSoup
import operator

city = '서울시'
dong = '종로구'
input_weather = f'{city} {dong} 날씨'
weather_url = f'https://search.naver.com/search.naver?query={input_weather}'
html = requests.get(weather_url).text
soup = BeautifulSoup(html, 'html.parser')
area = f'{city} {dong} 날씨입니다.'
print(f'{city} {dong} 날씨입니다.')
weather_temper = {}
weather_rainfall = {}
for i in range(8):
    hour = soup.select('.list_area li')[i].select_one('.item_time').text.strip()
    temper = soup.select('.list_area li')[i].select('.weather_item._dotWrapper')[0].text.strip()
    rainfall = soup.select('.info_list.rainfall._tabContent .list_area li')[i].select_one('dl dd').text.strip()
    if hour.split('시',1)[0] > '21':
        break;
    weather_temper[hour] = temper[:2]
    weather_rainfall[hour] = rainfall.split('%',1)[0]
wt_temper = sorted(weather_temper.items(), key=operator.itemgetter(1))
print(f'오늘의 최저온도는 {wt_temper[0][1]}도, '
      f'최고온도는 {wt_temper[-1][1]}도 입니다.')
wt_rainfall = sorted(weather_rainfall.items(), key=operator.itemgetter(1))

if wt_rainfall[-1][1] == '0':
    print('오늘은 맑음입니다.')
else:
    print(f'오늘의 강수확률은 {wt_rainfall[-1][0]} {wt_rainfall[-1][1]} 입니다.')
    if wt_rainfall[-1][1] >= '60':
        print('우산준비해주세요!!')

input_dust = f'{city} {dong} 미세먼지'
dust_url = f'https://search.naver.com/search.naver?query={input_dust}'
html1 = requests.get(dust_url).text
soup1 = BeautifulSoup(html1, 'html.parser')
dust = soup1.select('.state_info .figure')[0].text.strip()
avr_dust = soup1.select('.state_info .figure')[1].text.strip()
heavy_dust = soup1.select('.all_state .state_info .state')[0].text.strip()
if 0 <= int(dust[0:2]) < 30:
    dust_degree = '좋음'
elif 30 <= int(dust[0:2]) < 80:
    dust_degree = '보통'
elif 80 <= int(dust[0:2]) < 150:
    dust_degree = '나쁨'
else:
    dust_degree = '매우나쁨'
if 0 <= int(heavy_dust[0:2]) < 15:
    heavydust_degree = '좋음'
elif 15 <= int(heavy_dust[0:2]) < 35:
    heavydust_degree = '보통'
elif 35 <= int(heavy_dust[0:2]) < 75:
    heavydust_degree = '나쁨'
else:
    heavydust_degree = '매우나쁨'
if 0 <= int(avr_dust[0:2]) < 30:
    avr_dust_degree = '좋음'
elif 30 <= int(avr_dust[0:2]) < 80:
    avr_dust_degree = '보통'
elif 80 <= int(avr_dust[0:2]) < 150:
    avr_dust_degree = '나쁨'
else:
    avr_dust_degree = '매우나쁨'
print(f'현재 미세먼지는: {dust} {dust_degree}, 초미세먼지는: {heavy_dust} {heavydust_degree}'
      f'이고 1일 평균미세먼지는: {avr_dust} {avr_dust_degree}입니다.')
