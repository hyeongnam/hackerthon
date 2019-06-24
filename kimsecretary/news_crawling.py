import requests
from bs4 import BeautifulSoup
import datetime
from decouple import config
import sys

token = config('TOKEN')
api_url = f'https://api.telegram.org/bot{token}'


# 구글뉴스 검색어 속보, 최근 2시간 이내 기사
def news(text, chat_id):
    # text = '속보'
    hour = 1  # 최근 x시간 이내
    url = f'https://news.google.com/search?q={text}%20when%3A{hour}h&hl=ko&gl=KR&ceid=KR%3Ako'
    request = requests.get(url).text
    soup = BeautifulSoup(request, 'html.parser')

    news_list = soup.select(
        '#yDmH0d > c-wiz > div > div.FVeGwb.CVnAc > div.ajwQHc.BL5WZb.RELBvb > div > main > c-wiz > div.lBwEZb.BL5WZb.xP6mwf > div > div > article > h3 > a')
    news_time_list = soup.select(
        '#yDmH0d > c-wiz > div > div.FVeGwb.CVnAc > div.ajwQHc.BL5WZb.RELBvb > div > main > c-wiz > div.lBwEZb.BL5WZb.xP6mwf > div > div > article > div.QmrVtf.RD0gLb > div > time')

    news_url = []
    news_title = []
    news_time = []

    for nl in news_list:
        news_url.append('https://news.google.com' + nl.get('href')[1:])
        news_title.append(nl.text)

    for nt in news_time_list:
        date = nt.get('datetime')
        date = date.replace('T', ' ')
        date = date.replace('Z', '')
        date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        date = date + datetime.timedelta(hours=9)
        date = date.strftime("%H:%M")
        news_time.append(date)

    # for i in range(len(news_url)):
    for i in range(3):  # 일단 3개만 테스트
        msg = news_title[i] + ' [' + news_time[i] + ']\n' + news_url[i]
        requests.get(api_url + f'/sendMessage?chat_id={chat_id}&text={msg}')
