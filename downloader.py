import multiprocessing.process
import urllib.parse

import lxml
import lxml.html
import lxml.html.clean
import requests

BLACKLIST_QUERY_PARAMETERS = set()

REPLACE = {
    u'\xa0', '\n', '\t', '\r',
    '\u202a', '\u202b', '\u202c', '\u202d', '\u202e',
    '\u200e', '\u200f'
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Upgrade-Insecure-Requests': '1'
}


def optimise_text(text):
    s = text.casefold()

    for r in REPLACE:
        s = s.replace(r, ' ')

    return ' '.join(set(s.split()))


def format_url(url, source_url=None):
    url_split = urllib.parse.urlsplit(urllib.parse.unquote(url))

    query = {
        kv for kv in url_split.query.split('&') if (
                kv.split('=')[0].casefold() not in BLACKLIST_QUERY_PARAMETERS and
                kv != '')
    }

    if url_split.scheme != '':
        return urllib.parse.urlunsplit((url_split.scheme, url_split.netloc, url_split.path, '&'.join(query), ''))
    else:
        return urllib.parse.urljoin(source_url, url_split.path) + f'?{"&".join(query)}' if len(query) > 0 else ''


def get_website_data(url):
    r = None

    try:
        r = requests.get(url, headers=HEADERS, allow_redirects=True, timeout=3)
    except requests.exceptions.ReadTimeout:
        return {
            'r_url': url,
            's_url': url,
            'code': 'rq_timeout'
        }
    except requests.exceptions.SSLError:
        return {
            'r_url': url,
            's_url': url,
            'code': 'rq_ssl'
        }
    except requests.exceptions.ConnectionError:
        return {
            'r_url': url,
            's_url': url,
            'code': 'rq_connection'
        }

    if r.status_code != 200:
        return {
            'r_url': format_url(r.url),
            's_url': url,
            'code': str(r.status_code)
        }

    if not r.headers.get('content-type', '').startswith('text/html'):
        return {
            'r_url': format_url(r.url),
            's_url': url,
            'code': 'mf_type'
        }

    r.encoding = r.apparent_encoding

    parsed_html = lxml.html.fromstring(r.text)

    c_url = lxml.etree.XPath('//link[@rel="canonical"]/@href')(parsed_html)
    if len(c_url) > 0:
        c_url = c_url[0]

    r_url = format_url(r.url)

    links = set()
    for link in parsed_html.iterlinks():
        if link[1] == 'href':
            formatted_link = format_url(link[2], r_url)
            if (
                formatted_link != '' and
                formatted_link != r_url and
                formatted_link != url and
                formatted_link != c_url and
                    (':' not in formatted_link or formatted_link.startswith('http'))
            ):
                links.add(formatted_link)

    cleaner = lxml.html.clean.Cleaner(scripts=True, javascript=True, comments=True, style=True, inline_style=True)
    website_data = {
        'text': optimise_text(' '.join(lxml.etree.XPath('//text()')(cleaner.clean_html(parsed_html)))),
        'links': links,
        'r_url': r_url,
        's_url': url,
        'code': str(r.status_code)
    }

    if c_url:
        website_data['c_url'] = c_url

    return website_data
