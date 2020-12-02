from functools import partial
from os.path import basename, splitext
from urllib.parse import urlparse

from html5lib import parse
from httpx import ConnectTimeout
from trio import open_file

INDEX = 'https://thanhnien.vn/vaccine/'

parse_html5 = partial(parse, namespaceHTMLElements=False)


def articles(links):
    """Find URLs contains 'vacxin' in the given link."""
    for a in links:
        href = a.get('href')
        if href is None: continue
        url = 'http://thanhnien.vn/' + href
        if url.endswith('.html') and 'vac' in url: yield url


async def download(caption, url, dest, client):
    """The image and caption saved if contain information about vaccine"""
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
    """Search for img in the articles in order to download the images."""
    article = await client.get(url)
    for img in parse_html5(article.text).iterfind('.//img'):
        caption, url = img.get('alt'), img.get('data-src')
        if caption is None or ('vắc') not in caption.lower():
            if caption is None or ('vac') not in caption.lower(): continue
        if url is None: url = img.get('src')
        if url.endswith('logo.svg'): continue
        nursery.start_soon(download, caption, url, dest, client)


async def thanhnien(dest, client, nursery):
    """scrape image and captions optain from link."""
    index = await client.get(INDEX)
    for url in set(articles(parse_html5(index.text).iterfind('.//a'))):
        nursery.start_soon(scrape_images, url, dest/'thanhnien',
                           client, nursery)
