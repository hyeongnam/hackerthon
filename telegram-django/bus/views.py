import os
import re
import json

from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
# from django.shortcuts import render

import requests
from decouple import config
from bs4 import BeautifulSoup as BS

from .send_message import send_msg
from .models import BusGo, BusOut

token = config('TOKEN')
api_url = f'https://api.telegram.org/bot{token}'

reg_order = {}
routeid_list = []
save_input = {}
bus_len = {}
routeid = {}
station_include = []
user_msg = {}



@require_POST
@csrf_exempt
def tel(request):
    print('views tel')
    print('request=', request.body)
    global reg_order
    global routeid_list
    global save_input
    global routeid
    global station_include
    global user_msg
    global bus_len

    message = json.loads(request.body).get('message')
    chat_id = message.get('from').get('id')
    user_msg[chat_id] = message.get('text')
    # if message is not None:
    print('user_msg=', user_msg.get(chat_id))
    if user_msg.get(chat_id) is not None:
        # chat_id = message.get('from').get('id')  # 명시적으로 나타내기위해 get 사용 추천
        # input_text = message.get('text')
        # user_msg[chat_id] = input_text
        # text = input_text.split(' ')
        print('0 order=', reg_order.get(chat_id), 'save=', save_input.get(chat_id))

        if user_msg.get(chat_id)[-2:] in ['종료', '중지', '정지', '그만', '멈춰', ]:
            cron = f'sudo crontab -u {chat_id} -r'  # 해당 계정의 크론탭을 삭제 후
            user = f'sudo userdel -f {chat_id}'  # 계정을 삭제, 계정 먼저 삭제 시 크론탭 삭제 불가능
            os.system(cron)
            os.system(user)
            send_msg(chat_id, '버스 알림을 종료합니다.')
            # msg = '버스 알림을 종료합니다.'
            # requests.get(api_url + f'/sendMessage?chat_id={chat_id}&text={msg}')

        elif user_msg.get(chat_id)[-2:] == '등록' and reg_order.get(chat_id) is None:
            if reg_order.get(chat_id) is not None:
                del reg_order[chat_id]
            if user_msg.get(chat_id)[:2] == '출근':  # 등록을 입력 후 처음 메세지
                send_msg(chat_id, '버스 번호를 입력하세요 ex) 88-1, 88-1번')

                reg_order[chat_id] = 1  # 등록 1단계 버스 번호 입력 받기
                save_input[chat_id] = user_msg.get(chat_id)

                print('1 order=', reg_order.get(chat_id), 'save=', save_input.get(chat_id))

            # elif input_text[:2] == '퇴근':
            #     msg = '버스 번호를 입력하세요 ex) 88-1'
            #     requests.get(api_url + f'/sendMessage?chat_id={chat_id}&text={msg}')
            #     reg_order[chat_id] = 1  # 등록 1단계 버스 번호 입력 받기
        elif reg_order.get(chat_id) == 1 and save_input.get(chat_id) != user_msg.get(chat_id):  # 버스 번호 입력 받은 후 버스 선택
            # bus_number = re.findall('\d+-?\d+', input_text)[0]
            number = re.findall('\d+-?\d+', user_msg.get(chat_id))  # 메세지에서 숫자 또는 숫자-숫자만 추출
            if not number:
                number = re.findall('\d+', user_msg.get(chat_id))
            if not number:
                msg = '숫자를 포함해서 입력해주세요.\n' \
                      '버스 번호를 입력하세요 ex) 88-1, 88-1번'
                send_msg(chat_id, msg)

            else:
                bus_number = number[0]
                print('입력받은 버스넘버:', bus_number)
                url = f'http://openapi.gbis.go.kr/ws/rest/busrouteservice?serviceKey=p7RiOnONfT8hc4MMVfKU8%2BSr2pQ8vwgM3JQA0sap60em7nJZW5QpGUrGcDmQy4nqe%2B1YxAOAwL7F1uRrlk8PkQ%3D%3D&keyword={bus_number}'
                url_result = requests.get(url).text
                soup = BS(url_result, 'html.parser')
                bus_list = soup.find('msgbody')

                if not bus_list:
                    msg = '해당하는 버스가 없습니다.\n' \
                          '경기도를 경유하는 버스만 가능합니다.\n' \
                          '버스 번호를 입력하세요 ex) 88-1, 88-1번'
                    send_msg(chat_id, msg)
                    
                else:
                    msg = '버스를 선택하세요. ex) 1, 1번'
                    # requests.get(api_url + f'/sendMessage?chat_id={chat_id}&text={msg}')
                    for idx, bus in enumerate(bus_list):
                        msg += f'\n{idx + 1}. 지역: {bus.find("regionname").contents[0]} / 번호: {bus.find("routename").contents[0]}'
                        routeid_list.append(bus.find('routeid').contents[0])
                    send_msg(chat_id, msg)
                    bus_len[chat_id] = len(bus_list)

                    reg_order[chat_id] = 2
                    save_input[chat_id] = user_msg.get(chat_id)
                    print('2 order=', reg_order.get(chat_id), 'save=', save_input.get(chat_id), 'user_msg=',
                          user_msg.get(chat_id))

        elif reg_order.get(chat_id) == 2 and save_input.get(chat_id) != user_msg.get(chat_id):  # 버스 선택 후 탑승지 입력 받기
            # idx = int(re.findall('\d+', input_text)[0])
            idx = int(re.findall('\d+', user_msg.get(chat_id))[0])
            if idx < bus_len.get(chat_id):
                routeid[chat_id] = routeid_list[idx - 1]
                msg = '탑승 정류장이 포함된 단어를 입력하세요. \n ' \
                      'ex)시민의숲.양재꽃시장 -> 시민의숲, 양재, 꽃시장'
                send_msg(chat_id, msg)

                reg_order[chat_id] = 3
                save_input[chat_id] = user_msg.get(chat_id)
                print('3 order=', reg_order.get(chat_id), 'save=', save_input, 'user_msg=', user_msg.get(chat_id))
            else:
                msg = f'1~{len(routeid_list)}의 번호를 입력하세요'
                send_msg(chat_id, msg)

        elif reg_order.get(chat_id) == 3 and save_input.get(chat_id) != user_msg.get(chat_id):  # 입력받은 탑승지로 정류장 검색
            url = f'http://openapi.gbis.go.kr/ws/rest/busrouteservice/station?serviceKey=p7RiOnONfT8hc4MMVfKU8%2BSr2pQ8vwgM3JQA0sap60em7nJZW5QpGUrGcDmQy4nqe%2B1YxAOAwL7F1uRrlk8PkQ%3D%3D&routeId={routeid.get(chat_id)}'
            url_result = requests.get(url).text
            soup = BS(url_result, 'html.parser')
            station_list = soup.find('msgbody')

            index = 0
            station_list = list(station_list)

            for idx, station in enumerate(station_list):  # 정류장리스트에서 입력받은 단어가 포함된 정류장 찾기
                if user_msg.get(chat_id) in station.find('stationname').contents[0]:
                    if idx < len(station_list) - 1:
                        station_include.append([])
                        station_include[index].append(station.find('stationid').contents[0])
                        station_include[index].append(station.find('stationname').contents[0])
                        station_include[index].append(station_list[idx + 1].find('stationname').contents[0])
                        station_include[index].append(station.find('stationseq').contents[0])
                    index += 1
                    
            if not station_include: # 일치하는 정류장이 하나도 없는 경우
                msg = '입력한 단어가 포함된 정류장이 없습니다.\n' \
                      '탑승 정류장이 포함된 단어를 입력하세요. \n ' \
                      'ex)시민의숲.양재꽃시장 -> 시민의숲, 양재, 꽃시장'
                send_msg(chat_id, msg)
                # reg_order[chat_id] = 2
                # user_msg[chat_id] = save_input[chat_id]
                save_input[chat_id] = None

            else:
                msg = '탑승 정류장을 선택하세요. ex) 2, 2번\n' \
                      '     탑승 정류장  ->  다음 정류장 (운행방향)'
                for idx, station in enumerate(station_include):
                    if idx < len(station_include):
                        msg += f'\n{idx + 1}. {station[1]}  ->  {station[2]}'
                send_msg(chat_id, msg)
                reg_order[chat_id] = 4
                save_input[chat_id] = user_msg.get(chat_id)
            print('4 order=', reg_order.get(chat_id), 'save=', save_input.get(chat_id), 'user_msg=',
                  user_msg.get(chat_id))

        elif reg_order.get(chat_id) == 4 and save_input.get(chat_id) != user_msg.get(chat_id):
            # bus_stop = int(re.findall('\d+', input_text)[0])-1  # 1부터 출력했으므로 -1
            bus_stop = int(re.findall('\d+', user_msg.get(chat_id))[0]) - 1  # 1부터 출력했으므로 -1
            if bus_stop < len(station_include):
                # go_station_id = station_include[bus_stop][0]
                # go_route_id = routeid
                # go_station_order = station_include[bus_stop][3]
                # print(go_station_id, go_route_id, go_station_order)
                busgo = BusGo()
                busgo.chat_id = chat_id
                busgo.go_station_id = station_include[bus_stop][0]
                busgo.go_route_id = routeid.get(chat_id)
                busgo.go_station_order = station_include[bus_stop][3]
                busgo.save()
                # DB insert문 추가하기
                # bus_go_input(chat_id, go_station_id, go_route_id, go_station_order)
                send_msg(chat_id, '등록이 완료 되었습니다.')
                del reg_order[chat_id]

            else:
                msg = f'1~{len(station_include)}의 번호를 입력하세요'
                send_msg(chat_id, msg)
                save_input[chat_id] = None

            print('5 order=', reg_order.get(chat_id), 'save=', save_input)

        elif user_msg.get(chat_id)[:2] == '출근':
            print('@@@@@@@@@@@test1')
            if user_msg.get(chat_id)[-2:] != '등록':
                print('@@@@@@@@@@@test2')
                minute = re.findall('\d+', user_msg.get(chat_id))
                print('@@@@@@@@@@@test3 minute',minute)
                if not minute:
                    print('@@@@@@@@@@@pass')
                    pass
                else:
                    print('@@@@@@@@@@@else')

                    user = f'sudo useradd -d /home/ec2-user -u 500 -o {chat_id}'  # ec2-user 와 같은 uid 를 갖도록 계정 생성

                    # 크론탭 시간 1분은 좀 긴거 같고 30초 간격으로 수정해야할듯..
                    cron = f'(crontab -l 2>/dev/null; echo "*/1 * * * * python3 /home/ec2-user/telegram-django/bus_alarm.py {chat_id} {minute[0]} go") | sudo crontab -u {chat_id} -'
                    print(cron)
                    # cron = f'(crontab -l 2>/dev/null; echo "*/{minute} * * * * python3 ~/kim/bus_alarm.py {chat_id} {text[0]}") | crontab -'
                    os.system(user)
                    os.system(cron)
                    msg = f'출근 버스 도착 {minute[0]}분 전 알림\n' \
                        f'종료, 정지 등으로 종료할 수 있습니다.'
                    requests.get(api_url + f'/sendMessage?chat_id={chat_id}&text={msg}')
                    print('end')
    return JsonResponse({})
