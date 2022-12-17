import mimetypes

import requests
from bs4 import BeautifulSoup


class Scraper:
    def get_posts(self, url):
        body = requests.get(url).text
        soup = BeautifulSoup(body, 'html.parser')
        links = []
        for link in soup.find_all('a', {"class": "post-preview-link"}):
            links.append('https://danbooru.donmai.us' + link.attrs['href'])
        return links

    def get_post(self, url):
        body = requests.get(url).text
        soup = BeautifulSoup(body, 'html.parser')
        image_url = soup.find('li', {'id': 'post-info-size'}).contents[1].attrs['href']
        meta = {'image_name': url.split('/')[-1].split('?')[0]}
        tags = soup.find('section', {'class': 'image-container note-container'}).attrs['data-tags'].split()
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
        paginator = soup.find('a', {'class': 'paginator-next'})
        try:
            return 'https://danbooru.donmai.us' + paginator.attrs['href']
        except AttributeError:
            return None
