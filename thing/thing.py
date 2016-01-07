import os
import trello
import pprint

try:
    with open(os.environ.get('TRELLO_API_KEY', '.trello_api_key')) as f:
        key = f.readline().strip()
except FileNotFoundError:
    print('Get your Trello API key here: https://trello.com/app-key')
    with open(os.environ.get('TRELLO_API_KEY', '.trello_api_key'), 'w') as f:
        key = input('Please input your Trello api key: ')
        f.write(key)
finally:
    api = trello.TrelloApi(key)

try:
    with open(os.environ.get('TRELLO_TOKEN', '.trello_token')) as f:
        token = f.readline().strip()
except FileNotFoundError:
    url = api.get_token_url('Thing Doer', expires='30days', write_access=True)
    print('Get your Trello token here: {}'.format(url))
    with open(os.environ.get('TRELLO_TOKEN', '.trello_token'), 'w') as f:
        token = input('Please input your Trello token: ')
        f.write(token)
finally:
    api = trello.TrelloApi(key, token)



def run():
    for board in api.members.get_board('me'):
        print('{0[name]} - {0[url]}'.format(board))
