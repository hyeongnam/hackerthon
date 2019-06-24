from flask import Flask, request
import pprint
import requests
from decouple import config
import os
import re
from bs4 import BeautifulSoup as BS

app = Flask(__name__)

token = config('TOKEN')
api_url = f'https://api.telegram.org/bot{token}'


# select = ''


#   127.0.0.1/
@app.route("/")
def hello():
    return "Hello World!"


#   127.0.0.1/telegram
# @app.route('/telegram')
# def telegram2():
#     send_message('함수 전달 완료')
#     return '전송완료'
select = ''
crawling = ''
reg_order = {}


@app.route(f'/{token}', methods=['POST'])
def telegram():
    pprint.pprint(request.get_json())
    message = request.get_json().get('message')
    print(message)
    global select
    global crawling
    global reg_order

    if message is not None:
        chat_id = message.get('from').get('id')  # 명시적으로 나타내기위해 get 사용 추천
        input_text = message.get('text')

        # text = input_text.split(' ')
        if input_text[-2:] in ['종료', '중지', '정지', '그만', '멈춰', ]:
            cron = f'sudo crontab -u {chat_id} -r'  # 해당 계정의 크론탭을 삭제 후
            user = f'sudo userdel -f {chat_id}'  # 계정을 삭제, 계정 먼저 삭제 시 크론탭 삭제 불가능
            os.system(cron)
            os.system(user)
            msg = '버스 알림을 종료합니다.'
            requests.get(api_url + f'/sendMessage?chat_id={chat_id}&text={msg}')

        elif input_text[:2] == '출근':
            if input_text[-2:] == '등록':
                msg = '버스 번호를 입력하세요 ex) 88-1'
                requests.get(api_url + f'/sendMessage?chat_id={chat_id}&text={msg}')
                reg_order[f'{chat_id}_order'] = 1  # 등록 1단계 버스 번호 입력 받기

            minute = re.findall('\d+', input_text)
            print(minute)
            user = f'sudo useradd -d /home/ec2-user -u 500 -o {chat_id}'  # ec2-user 와 같은 uid 를 갖도록 계정 생성
            # 크론탭 시간 1분은 좀 긴거 같고 30초 간격으로 수정해야할듯..
            cron = f'(crontab -l 2>/dev/null; echo "*/1 * * * * python3 /home/ec2-user/kim/bus_alarm.py {chat_id} {minute[0]}") | sudo crontab -u {chat_id} -'
            # cron = f'(crontab -l 2>/dev/null; echo "*/{minute} * * * * python3 ~/kim/bus_alarm.py {chat_id} {text[0]}") | crontab -'
            os.system(user)
            os.system(cron)
            msg = f'출근 버스 도착 {minute[0]}분 전 알림\n' \
                f'종료, 정지 등으로 종료할 수 있습니다.'
            requests.get(api_url + f'/sendMessage?chat_id={chat_id}&text={msg}')
            print('end')

        elif reg_order[f'{chat_id}_order'] == 1:  # 버스 번호 입력 받은 후 단계
            bus_number = re.findall('\d+-?\d+', input_text)
            url = f'http://openapi.gbis.go.kr/ws/rest/busrouteservice?serviceKey=p7RiOnONfT8hc4MMVfKU8%2BSr2pQ8vwgM3JQA0sap60em7nJZW5QpGUrGcDmQy4nqe%2B1YxAOAwL7F1uRrlk8PkQ%3D%3D&keyword={bus_number}'
            url_result = requests.get(url).text
            soup = BS(url_result, 'html.parser')
            bus_list = soup.find('msgbody')

            routeid_list = []
            msg = '버스를 선택하세요. ex) 1, 1번'
            requests.get(api_url + f'/sendMessage?chat_id={chat_id}&text={msg}')

            for idx, bus in enumerate(bus_list):
                msg = f'{idx + 1}. 지역 : {bus.find("regionname").contents[0]}\n' \
                    f'   번호:{bus.find("routename").contents[0]}'
                routeid_list.append(bus.find('routeid').contents[0])
                requests.get(api_url + f'/sendMessage?chat_id={chat_id}&text={msg}')


        # if text[0] == '뉴스':
        #     news('속보', chat_id)

        # if text[ 2] == '시작':
        #     pass
        #     #news(text[1])
        #     # 크롤링 시작
        #
        # elif text[2] in ['정지', '중단', '중지', '그만']:
        #     pass
        # if text[0:2] == '버스':
        #     if text[-2:] == '시작':
        #         select = 'bus'
        #
        #         msg = '''
        #                 승차 정류장을 선택하세요
        #             1. 강남역나라빌딩앞
        #             2. 수원버스터미널
        #             3. 경기도 문화의전당
        #         '''
        #         requests.get(api_url + f'/sendMessage?chat_id={chat_id}&text={msg}')
        #     elif text[-2:] in ['정지', '중단', '중지', '그만']:
        #         select = ''
        #         msg = '버스 알림을 정지합니다'
        #         requests.get(api_url + f'/sendMessage?chat_id={chat_id}&text={msg}')
        #
        # elif select == 'bus' and text[0] == '1':
        #     msg = '3007번 14분전 7정거장 22석'
        #     requests.get(api_url + f'/sendMessage?chat_id={chat_id}&text={msg}')
        #     time.sleep(5)
        #     msg = '3007번 8분전 4정거장 15석'
        #     requests.get(api_url + f'/sendMessage?chat_id={chat_id}&text={msg}')
        #     time.sleep(5)
        #     msg = '3007번 3분전 2정거장 10석'
        #     requests.get(api_url + f'/sendMessage?chat_id={chat_id}&text={msg}')
        #     select = ''
        #
        # elif text[0:3] == '크롤링':
        #     if text[-2:] == '시작':
        #         select = 'crawling'
        #         msg = '''
        #             크롤링할 사이트를 선택하세요
        #             1. OKKY
        #             2. devkorea
        #             3. devpia
        #         '''
        #         requests.get(api_url + f'/sendMessage?chat_id={chat_id}&text={msg}')
        #     elif text[-2:] in ['정지', '중단', '중지', '그만']:
        #         select = ''
        #         msg = '크롤링을 정지합니다.'
        #         requests.get(api_url + f'/sendMessage?chat_id={chat_id}&text={msg}')
        # elif select == 'crawling' and text[0] == '1':
        #     msg = '크롤링할 단어를 입력하세요'
        #     requests.get(api_url + f'/sendMessage?chat_id={chat_id}&text={msg}')
        # elif select == 'crawling':
        #     crawling = text
        #     msg = f'{crawling}이 포함된 글이 올라오면 알려드릴게요!'
        #     requests.get(api_url + f'/sendMessage?chat_id={chat_id}&text={msg}')
        #     time.sleep(5)
        #     msg = '''KB-KISA 핀테크 해커톤 관심있으신분 있으실까요?
        #             https://okky.kr/article/590299
        #         '''
        #     requests.get(api_url + f'/sendMessage?chat_id={chat_id}&text={msg}')
        #     time.sleep(5)
        #     msg = '''2019 서울 통합이동서비스(MaaS) 해커톤 참가자 모집(~5/3)
        #         https://okky.kr/article/572953
        #         '''
        #     requests.get(api_url + f'/sendMessage?chat_id={chat_id}&text={msg}')

        # requests.get(api_url + f'/sendMessage?chat_id={chat_id}&text={text}')
        # requests.get(api_url + f'/sendMessage?chat_id={chat_id}&text={msg}')

    return '', 200


# app.py 파일이 `python app.py`로시작 되었을 때 작용
if __name__ == '__main__':
    app.run(debug=True)  # 서버가 켜져 있는 동안 수정이 발생하면 자동으로 재시작
