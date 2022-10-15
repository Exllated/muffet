import os

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Upgrade-Insecure-Requests': '1'
}

CONFIG_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data_config')
DATA_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data_db')

BLACKLIST_QUERY = None
BLACKLIST_NETLOCS = None
BLACKLIST_IN_URL = None

BLACKLIST_SYMBOLS = (
    u'\xa0', '\n', '\t', '\r',
    '\u202a', '\u202b', '\u202c', '\u202d', '\u202e',
    '\u200e', '\u200f'
)


def load():
    global BLACKLIST_QUERY
    global BLACKLIST_NETLOCS
    global BLACKLIST_IN_URL
    global BLACKLIST_SYMBOLS

    BLACKLIST_QUERY = read_file_lines_as_tuple(os.path.join(CONFIG_DIR, 'blacklist_query'))
    BLACKLIST_NETLOCS = read_file_lines_as_tuple(os.path.join(CONFIG_DIR, 'blacklist_netlocs'))
    BLACKLIST_IN_URL = read_file_lines_as_tuple(os.path.join(CONFIG_DIR, 'blacklist_in_url'))

    blacklist_symbols_path = os.path.join(CONFIG_DIR, 'blacklist_symbols')
    create_file_if_not_exist(blacklist_symbols_path)
    with open(blacklist_symbols_path, 'r') as f:
        BLACKLIST_SYMBOLS = BLACKLIST_SYMBOLS + tuple(f.read().replace('\n', '').replace(' ', ''))
        pass

    pass


def create_file_if_not_exist(path):
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(path)

    if not os.path.exists(path):
        with open(path, 'w') as f:
            pass
    pass


def read_file_lines_as_tuple(path):
    create_file_if_not_exist(path)
    with open(path, 'r') as f:
        lines = set(f.read().split('\n'))  # conversion to set for deduplication
        if len(lines) == 1 and list(lines)[0] == '':
            return tuple()  # return empty tuple so other functions dependent on 'for _ in _' won't return ''
        return tuple(lines)
