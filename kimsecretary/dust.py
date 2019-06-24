import requests
from bs4 import BeautifulSoup


city = '서울시'
dong = '강남구'
input_dust = f'{city} {dong} 미세먼지'
dust_url = f'https://search.naver.com/search.naver?query={input_dust}'
html = requests.get(dust_url).text
soup = BeautifulSoup(html, 'html.parser')
dust = soup.select('.state_info .figure')[0].text.strip()
avr_dust = soup.select('.state_info .figure')[1].text.strip()
heavy_dust = soup.select('.all_state .state_info .state')[0].text.strip()
print(dust, avr_dust, heavy_dust)