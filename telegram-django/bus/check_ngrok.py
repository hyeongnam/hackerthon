import json
import requests


# def get_ngrok_url():
url = "http://localhost:4040/api/tunnels/"
res = requests.get(url)
res_unicode = res.content.decode("utf-8")
res_json = json.loads(res_unicode)
for i in res_json["tunnels"]:
    if i['name'] == 'command_line':
        print(i['public_url'])
