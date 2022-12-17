import mimetypes

import requests
from bs4 import BeautifulSoup


class Scraper:
    def get_posts(self, url):
        body = requests.get(url).text
        soup = BeautifulSoup(body, 'html.parser')
        links = []
        for span in soup.find_all('span', {"class": "thumb"}):
            links.append('https://safebooru.org/' + span.contents[0].attrs['href'])
        return links

    def get_post(self, url):
        body = requests.get(url).text
        soup = BeautifulSoup(body, 'html.parser')
        image_url = soup.find('meta', {'property': 'og:image'}).attrs['content']
        meta = {'image_name': url.split('id=')[-1]}
        tags = soup.find('textarea', {'id': 'tags'}).contents[0].text.split()
        meta['tags'] = tags
        r = requests.get(image_url, stream=True)
        if r.status_code == 200:
            r.raw.decode_content = True
            meta['ext'] = mimetypes.guess_extension(r.headers['content-type'])
            return r.raw, meta
        else:
            print(f'Got {r.status_code} for {url}')

    def next_page(self, url):
        body = requests.get(url).text
        soup = BeautifulSoup(body, 'html.parser')
        pagination = soup.find('div', {'class': 'pagination'})
        next_pg = pagination.find('a', {'alt': 'next'})
        if next_pg:
            next_pg = 'https://safebooru.org/index.php' + next_pg.attrs['href']
        return next_pg
