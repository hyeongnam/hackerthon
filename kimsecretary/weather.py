import requests
from bs4 import BeautifulSoup

url = 'https://weather.naver.com/rgn/townWetr.nhn?naverRgnCd=09680101'
html = requests.get(url).text
soup = BeautifulSoup(html, 'html.parser')
date = soup.select('.w_now2 ul li h5')[0].text.strip()
weather = soup.select('.w_now2 ul li em')[0].text.strip()
weather_than0 = soup.select('.w_now2 ul li p .temp')[0].text.strip()
weather_than = f'어제보다 {weather_than0}'
rain0 = soup.select('.w_now2 ul li p')[0].text.split("|")[1].split("%")[0].strip()
rain = f'{rain0}%'
dust = soup.select('.w_now2 ul li p a span')[0].text.strip()
dust_num = soup.select('#ly_atm dl dt span')[0].text.strip()
print(date)
print(weather)
print(weather_than)
print(rain)
print(dust,dust_num)