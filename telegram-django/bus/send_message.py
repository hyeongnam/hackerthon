from decouple import config
import requests


def send_msg(chat_id, msg):
    token = config('TOKEN')
    api_url = f'https://api.telegram.org/bot{token}'
    requests.get(api_url + f'/sendMessage?chat_id={chat_id}&text={msg}')
