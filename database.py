import os.path
import urllib.parse
from configs import DATA_DIR, CONFIG_DIR

ERROR_LISTS_DIR = os.path.join(DATA_DIR, 'error')
DOWNLOAD_DIR = os.path.join(DATA_DIR, 'download')

URL_TYPES = ('r_url', 's_url', 'c_url')


def write_website_data(website_data):
    if website_data['code'] != '200':
        add_lines_to_file(os.path.join(ERROR_LISTS_DIR, website_data['code']),
                          {website_data[url_type] for url_type in URL_TYPES if website_data.get(url_type)})
        return

    path = url_to_db_path(website_data['r_url'], website_data.get('c_url'))

    backlinks = {website_data[url_type] for url_type in URL_TYPES if website_data.get(url_type)}

    if os.path.exists(path):
        with open(path, 'r') as f:
            backlinks.update(f.read().split('\n\n')[0].split('\n'))

    file_dir = os.path.dirname(path)
    if not os.path.isdir(file_dir):
        os.makedirs(file_dir, exist_ok=True)

    with open(path, 'w') as f:
        backlinks_string = '\n'.join(backlinks)
        links_string = '\n'.join(website_data['links'])
        f.write(
            f'{backlinks_string}\n\n'
            f'{links_string}\n\n'
            f'{website_data["text"]}'
        )
    pass


def add_lines_to_file(path, new_lines):
    lines = set(new_lines)
    if os.path.exists(path):
        with open(path, 'r') as f:
            lines.update(f.read().split('\n'))

    with open(path, 'w') as f:
        f.write('\n'.join(lines))
    pass


def url_to_db_path(r_url, c_url=None):
    url_split = urllib.parse.urlsplit(c_url if c_url else r_url)
    return os.path.join(DOWNLOAD_DIR, os.path.join(url_split.netloc, url_split.path[1:], url_split.query).strip('/')) + '.mf'
