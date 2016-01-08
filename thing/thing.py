import json
import logging
import os
import pprint
import tempfile
import time
import trello
from collections import namedtuple
from contextlib import contextmanager
from functools import lru_cache

logging.basicConfig(filename='thing.log',
                    format='%(asctime)s:%(levelname)s:%(name)s:%(message)s',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.info('{:*^80.80}'.format(' starting things '))


@lru_cache()
def get_connection():
    '''
    Connect to the trello API and return a TrelloApi instance.

    If no ``.trello_api_key`` or ``.trello_token`` exist, ask the user
    for their api key/token and create the missing files.
    '''
    try:
        logger.debug('Reading api key...')
        with open(os.environ.get('TRELLO_API_KEY', '.trello_api_key')) as f:
            key = f.readline().strip()
    except FileNotFoundError:
        print('Get your Trello API key here: https://trello.com/app-key')
        with open(os.environ.get('TRELLO_API_KEY', '.trello_api_key'), 'w') as f:
            key = input('Please input your Trello api key: ')
            f.write(key)
    finally:
        api = trello.TrelloApi(key)
        logger.debug('api key OK')

    try:
        logger.debug('Reading token...')
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
        logger.info('token OK')
    return api


@contextmanager
def load_config():
    '''
    # TODO: Rename thing.json -W. Werner, 2016-01-08
    Load config from thing.json. If no file exists, create it. If file exists
    but is unusable, back it up and display backup location and create a new
    file.
    
    When context exits, save config.
    '''

    config = {}
    try:
        with open('thing.json') as f:
            config = json.load(f)
    except FileNotFoundError:
        pass # cause we're going to create it later
    except json.decoder.JSONDecodeError:
        with tempfile.NamedTemporaryFile(prefix='thing', suffix='.json') as t,\
                open('thing.json', 'rb') as f:
            print('Unable to load thing.json, backing up to {}'.format(t.name))
            t.write(f.read())

    try:
        yield config
    finally:
        with open('thing.json', 'w') as f:
            json.dump(config, f)


def create_thing_board():
    '''
    # TODO: Rename board to something else -W. Werner, 2016-01-08
    Create board Thing and return board id
    '''
    logger.debug('Geting connnection')
    api = get_connection()

    logger.info('Creating new board %r', 'Thing')
    board = api.boards.new('Thing')
    logger.debug('Board info: %r', board)

    return board['id']


class Board:
    def __init__(self, id):
        logger.debug('Creating board with id %r...', id)
        api = get_connection()
        self._json = api.boards.get(id)

        logger.debug('Getting cards...')
        self._cards = api.boards.get_card(id, fields=['idList',
                                                      'name',
                                                      'url',
                                                      ])
        logger.debug('Got %d cards', len(self._cards))

        logger.debug('Getting lists...')
        self._lists = api.boards.get_list(id, fields=['name'])
        logger.debug('Got %d lists', len(self._lists))


def run():
    start = time.time()
    logger.debug('Running the things!')
    with load_config() as config:
        api = get_connection()
        board_id = config.get('board_id')
        if board_id is None:
            board_id = config['board_id'] = create_thing_board()
        else:
            logger.debug('Getting board')
            board = Board(board_id)
            lists = api.boards.get_list(board_id)
            logger.debug("Here's your lists: %r", lists)
    logger.info('Done in %.2fs', time.time()-start)
