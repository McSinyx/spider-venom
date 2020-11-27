from functools import partial
from os.path import basename, splitext
from urllib.parse import urlparse

from html5lib import parse
from httpx import ConnectTimeout
from trio import open_file

INDEX = 'https://tuoitre.vn/vaccine.html'

parse_html5 = partial(parse, namespaceHTMLElements=False)


def articles(links):
    for a in links:
        href = a.get('href')
        if href is None: continue
        url = 'http://tuoitre.vn' + href
        if url.endswith('.htm') and 'vac' in url: yield url


async def download(img, dest, client):
    caption, url = img.get('alt'), img.get('src')
    name, ext = splitext(basename(urlparse(url).path))
    directory = dest / name
    await directory.mkdir(parents=True, exist_ok=True)

    try:
        fi = await client.get(url)
    except ConnectTimeout:
        return
    async with await open_file(directory/f'image{ext}', 'wb') as fo:
        async for chunk in fi.aiter_bytes(): await fo.write(chunk)
    await (directory/'caption').write_text(caption, encoding='utf-8')
    print(caption)


async def scrape_images(url, dest, client, nursery):
    article = await client.get(url)
    for img in parse_html5(article.text).iterfind('.//img'):
        if img.get('type') == 'photo':
            nursery.start_soon(download, img, dest, client)


async def tuoitre(dest, client, nursery):
    index = await client.get(INDEX)
    for url in set(articles(parse_html5(index.text).iterfind('.//a'))):
        nursery.start_soon(scrape_images, url, dest/'tuoitre',
                           client, nursery)
