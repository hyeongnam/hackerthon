import requests
from decouple import config


def send_message(text):
    token = config('TOKEN')
    api_url = f'https://api.telegram.org/bot{token}'

    # 내가 챗봇에 보낸 메세지를 통해 나의 id를 알아내고 내 id로 메세지를 보낸다.
    updates = requests.get(api_url + '/getUpdates').json()  # 일정시간이 지나면 업데이트 내역에 삭제된다.
    print(updates)
    chat_id = updates['result'][0]['message']['from']['id']

    requests.get(api_url + f'/sendMessage?chat_id={chat_id}&text={text}')

    print(chat_id)

