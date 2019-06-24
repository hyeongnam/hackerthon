from decouple import config
token = config('TOKEN')
api_url = f'https://api.telegram.org/bot{token}'
webhook_url = input()

print(f'{api_url}/setWebhook?url={webhook_url}/{token}')
