# Dantri vaccine image scraper
# Copyright (C) 2020  Lê Huy Quang
#
# This file is part of Spider Venom.
#
# Spider Venom is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Spider Venom is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Spider Venom.  If not, see <https://www.gnu.org/licenses/>.

from functools import partial
from os.path import basename, splitext

from html5lib import parse
from httpx import ConnectError, ConnectTimeout
from trio import open_file

INDEX = 'https://dantri.com.vn/vaccine.tag'

parse_html5 = partial(parse, namespaceHTMLElements=False)


def articles(links):
    """Search for URLs contains 'vacxin' in the given link."""
    for a in links:
        href = a.get('href')
        if href is None: continue
        if href.startswith('http'):
            url = href
        else:
            url = 'https://dantri.com.vn' + href
        if url.endswith('.htm') and 'vac' in url:
            yield url


async def download(caption, url, dest, client):
    """Save the given image with caption if it's about vaccine."""
    name, ext = splitext(basename(url))
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
    """Download vaccine images from the given Dantri article."""
    try:
        article = await client.get(url)
    except ConnectError:
        print(url)
        return
    for img in parse_html5(article.text).iterfind('.//img'):
        caption, url = img.get('alt'), img.get('src')
        if caption is None: continue
        if 'vac' in caption.lower() or 'vắc' in caption.lower():
            nursery.start_soon(download, caption, url, dest, client)


async def dantri(dest, client, nursery):
    """Scraping images and their captions from the given link."""
    index = await client.get(INDEX)
    for url in set(articles(parse_html5(index.text).iterfind('.//a'))):
        nursery.start_soon(scrape_images, url, dest/'dantri',
                           client, nursery)
