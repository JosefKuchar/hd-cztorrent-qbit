# VERSION: 1.00
# AUTHORS: Josef Kuchař (josef@josefkuchar.com)

from helpers import download_file, retrieve_url
from novaprinter import prettyPrinter
from html.parser import HTMLParser
import requests
import tempfile
import os
import io
import gzip
import configparser
from urllib.parse import unquote
from bs4 import BeautifulSoup

class hd_cztorrent(object):
    url = 'https://www.hd-cztorrent.cz/'
    name = 'HD CZTORRENT'
    supported_categories = {'all': '0', 'movies': '6', 'tv': '4',
                            'music': '1', 'games': '2', 'anime': '7', 'software': '3'}

    def __init__(self):
        # Load config
        config = configparser.ConfigParser()
        config.read(os.path.dirname(os.path.abspath(__file__)) + '/hd_cztorrent.txt')

        login = {
            'uid': config['LOGIN']['username'],
            'pwd': config['LOGIN']['password']
        }

        # Create cookie requests session
        self.session = requests.Session()

        # Login
        self.session.post(
            'https://www.hd-cztorrent.cz/index.php?page=login', data=login)

    def download_torrent(self, info):
        file, path = tempfile.mkstemp()
        file = os.fdopen(file, "wb")
        # Download url
        response = self.session.get(info)
        dat = response.content
        # Check if it is gzipped
        if dat[:2] == b'\x1f\x8b':
            # Data is gzip encoded, decode it
            compressedstream = io.BytesIO(dat)
            gzipper = gzip.GzipFile(fileobj=compressedstream)
            extracted_data = gzipper.read()
            dat = extracted_data

        # Write it to a file
        file.write(dat)
        file.close()
        # return file path
        print(path + " " + info)

    def search(self, what, cat='all'):
        response = self.session.get(
            'https://www.hd-cztorrent.cz/index.php?page=torrents&search={}&category=0&uploader=0&options=0&active=0&gold=0'.format(what))
        response.encoding = 'utf-8'

        soup = BeautifulSoup(response.text, 'html.parser')
        form = soup.find('form', {'name': 'deltorrent'})
        torrents = form.findAll('td', {'onmouseover': "this.className='post'"})

        for torrent in torrents:
            details = {}

            t = torrent.find_parent('tr')

            info = t.findAll('td', {'class': 'lista'})

            details_name = info[1].find('a')
            print(details_name.getText())
            details['name'] = details_name.getText()
            details['desc_link'] = 'https://www.hd-cztorrent.cz/' + details_name['href']
            details['link'] = 'https://www.hd-cztorrent.cz/' + info[3].find('a')['href']
            details['size'] = info[8].getText()
            counts = t.findAll('td', {'width': '30'})
            details['seeds'] = counts[0].getText()
            details['leech'] = counts[1].getText()
            details['engine_url'] = 'https://www.hd-cztorrent.cz/'

            prettyPrinter(details)
