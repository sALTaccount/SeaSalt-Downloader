import io
import mimetypes
import time

# import requests
import httpx
from bs4 import BeautifulSoup


class Scraper:

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/110.0",
    }

    image_headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/110.0",
    }

    def get_posts(self, url, parallel, args):
        body = httpx.Client(http2=True).get(url, headers=self.headers).content
        soup = BeautifulSoup(body, 'html.parser')
        images = []
        for image in soup.find_all('img', {"class": "imageFade"}):
            images.append(image.attrs['src'])
        return images

    def get_post(self, url, parallel, args):
        try:
            with httpx.Client(http2=True) as client:
                meta = {'image_name': url.split('/')[-1].split('=')[0].split('.')[0]}
                image_url = url.replace('moviethumbs', 'mvcdn')
                response = client.get(image_url, headers=self.image_headers)
                if response.status_code == 200:
                    meta['ext'] = mimetypes.guess_extension(response.headers['content-type'])
                    stream = io.BytesIO(response.content)
                    return stream, meta
                else:
                    print(f'Got {response.status_code} for {image_url}')

        except Exception as e:
            return None, None

    def next_page(self, url, parallel, args):
        body = httpx.Client(http2=True).get(url, headers=self.headers).text
        soup = BeautifulSoup(body, 'html.parser')
        paginator = soup.find('ul', {'class': 'pagination'})
        try:
            page = paginator.contents[-2].contents[1].attrs['href']
            return 'https://fancaps.net/movies/' + page if page and page != '#' else None
        except AttributeError:
            return None
