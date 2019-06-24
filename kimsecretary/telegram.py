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
# select = ''
# crawling = ''
reg_order = {}
routeid_list = []
save_input = ''
routeid = ''
station_include = []


@app.route(f'/{token}', methods=['POST'])
def telegram():
    global reg_order
    global routeid_list
    global save_input
    global routeid
    global station_include
    # global pre_text

    pprint.pprint(request.get_json())
    # if request.get_json().get('message').get('text') != pre_message:
    message = request.get_json().get('message')

    if message is not None:
        chat_id = message.get('from').get('id')  # 명시적으로 나타내기위해 get 사용 추천
        input_text = message.get('text')

        # text = input_text.split(' ')
        print('0 order=',reg_order.get(chat_id), 'save=',save_input)

        if input_text[-2:] in ['종료', '중지', '정지', '그만', '멈춰', ]:
            cron = f'sudo crontab -u {chat_id} -r'  # 해당 계정의 크론탭을 삭제 후
            user = f'sudo userdel -f {chat_id}'  # 계정을 삭제, 계정 먼저 삭제 시 크론탭 삭제 불가능
            os.system(cron)
            os.system(user)
            msg = '버스 알림을 종료합니다.'
            requests.get(api_url + f'/sendMessage?chat_id={chat_id}&text={msg}')

        elif input_text[-2:] == '등록' and reg_order.get(chat_id) is None:
            if input_text[:2] == '출근':  # 등록을 입력 후 처음 메세지
                msg = '버스 번호를 입력하세요 ex) 88-1, 88-1번'
                requests.get(api_url + f'/sendMessage?chat_id={chat_id}&text={msg}')

                reg_order[chat_id] = 1  # 등록 1단계 버스 번호 입력 받기
                save_input = input_text
                print('등록일 때 reg_order=', reg_order)
                print('1 order=', reg_order.get(chat_id), 'save=', save_input)



            # elif input_text[:2] == '퇴근':
            #     msg = '버스 번호를 입력하세요 ex) 88-1'
            #     requests.get(api_url + f'/sendMessage?chat_id={chat_id}&text={msg}')
            #     reg_order[chat_id] = 1  # 등록 1단계 버스 번호 입력 받기
        elif reg_order.get(chat_id) == 1 and save_input != input_text:  # 버스 번호 입력 받은 후 버스 선택
            bus_number = re.findall('\d+-?\d+', input_text)[0]
            print('입력받은 버스넘버:', bus_number)
            url = f'http://openapi.gbis.go.kr/ws/rest/busrouteservice?serviceKey=p7RiOnONfT8hc4MMVfKU8%2BSr2pQ8vwgM3JQA0sap60em7nJZW5QpGUrGcDmQy4nqe%2B1YxAOAwL7F1uRrlk8PkQ%3D%3D&keyword={bus_number}'
            url_result = requests.get(url).text
            soup = BS(url_result, 'html.parser')
            bus_list = soup.find('msgbody')

            msg = '버스를 선택하세요. ex) 1, 1번'
            # requests.get(api_url + f'/sendMessage?chat_id={chat_id}&text={msg}')
            for idx, bus in enumerate(bus_list):
                msg += f'\n{idx + 1}. 지역 : {bus.find("regionname").contents[0]}/번호:{bus.find("routename").contents[0]}'
                routeid_list.append(bus.find('routeid').contents[0])
            requests.get(api_url + f'/sendMessage?chat_id={chat_id}&text={msg}')
            reg_order[chat_id] = 2
            save_input = input_text
            print('2 order=', reg_order.get(chat_id), 'save=', save_input)

        elif reg_order.get(chat_id) == 2 and save_input != input_text:  # 버스 선택 후 탑승지 입력 받기
            idx = int(re.findall('\d+', input_text)[0])
            routeid = routeid_list[idx-1]
            msg = '탑승 정류장이 포함된 단어를 입력하세요. \n ' \
                'ex)시민의숲.양재꽃시장 -> 시민의숲, 양재, 꽃시장'
            requests.get(api_url + f'/sendMessage?chat_id={chat_id}&text={msg}')
            reg_order[chat_id] = 3
            save_input = input_text
            print('3 order=', reg_order.get(chat_id), 'save=', save_input)

        elif reg_order.get(chat_id) == 3 and save_input != input_text:
            url = f'http://openapi.gbis.go.kr/ws/rest/busrouteservice/station?serviceKey=p7RiOnONfT8hc4MMVfKU8%2BSr2pQ8vwgM3JQA0sap60em7nJZW5QpGUrGcDmQy4nqe%2B1YxAOAwL7F1uRrlk8PkQ%3D%3D&routeId={routeid}'
            url_result = requests.get(url).text
            soup = BS(url_result, 'html.parser')
            station_list = soup.find('msgbody')

            print('station_list=', station_list)

            index = 0
            station_list = list(station_list)

            for idx, station in enumerate(station_list):
                if input_text in station.find('stationname').contents[0]:
                    if idx <= len(station_list):
                        station_include.append([])
                        station_include[index].append(station.find('stationid').contents[0])
                        station_include[index].append(station.find('stationname').contents[0])
                        station_include[index].append(station_list[idx + 1].find('stationname').contents[0])
                        station_include[index].append(station.find('stationseq').contents[0])
                    index += 1
            msg = '탑승 정류장을 선택하세요. ex) 2, 2번\n' \
                  '     탑승 정류장  ->  다음 정류장 (운행방향)'
            for idx, station in enumerate(station_include):
                msg += f'\n{idx+1}. {station[1]}  ->  {station[2]}'
            requests.get(api_url + f'/sendMessage?chat_id={chat_id}&text={msg}')
            reg_order[chat_id] = 4
            save_input = input_text
            print('4 order=', reg_order.get(chat_id), 'save=', save_input)

        elif reg_order.get(chat_id) == 4 and save_input != input_text:
            msg = '등록이 완료 되었습니다.'
            requests.get(api_url + f'/sendMessage?chat_id={chat_id}&text={msg}')
            del reg_order[chat_id]
            print('5 order=', reg_order.get(chat_id), 'save=', save_input)

        elif input_text[:2] == '출근':
            if input_text[-2:] != '등록':
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
