Scraping vaccine images from Dantri
===================================

Site analysis
-------------

The site I used to work with to get the articles, download and scrape images about vaccine is::

   https://dantri.com.vn/vaccine.tag

The href provided in ``<a>`` can't directly link to the articles, some ``<a>`` have none of href attribute and some ``<a>`` have href start with http. For example:

.. code-block:: html

   <figure class="image align-center" contenteditable="false">
   <img title="Bill Gates dự đoán tới hết năm 2022 dịch Covid-19 mới chấm dứt - 1" src="https://icdn.dantri.com.vn/thumb_w/640/2020/08/11/covid-1597127036692.jpg" 
        alt="Bill Gates dự đoán tới hết năm 2022 dịch Covid-19 mới chấm dứt - 1" data-width="800" data-height="450"data-original="https://icdn.dantri.com.vn/2020/08/11/covid-1597127036692.jpg" data-photo-id="1034257" />


For the images and captions in the articles, we will get the ``src``---image source and ``alt`` tag.


Scraping Explaination
---------------------

Define the site as :

.. code-block:: python

  INDEX = 'https://dantri.com.vn/vaccine.tag'

The scraper will be focused on three main functions ``download()``, ``scrape_images()`` and ``articles()``.


articles()
^^^^^^^^^^

.. code-block:: python

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

``<a>`` tags try to get the href attribute of each ``<a>`` tag. Since some ``<a>`` don't have an href attribute, we will ignore if href returns None. To make href a recognized url, we add ``http://dantri.com.vn`` in advance href. If href start with ``http``, we add url as href else we add url in advance href  .Finally, to get vaccine-relevant articles, we just get the end of the url with ``.htm`` and contains ``vac``.

download()
^^^^^^^^^^

.. code-block:: python

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

This code will download the image from ``src`` and the caption from ``alt``. First I use ``name, ext = splitext(basename(url))`` to split url to find image name and extension. Then each image and its caption is then put in the same folder.

scrape_images()
^^^^^^^^^^^^^^^

.. code-block:: python

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

First, I try to get url of article from client, except Connection is error then i show the url. The appropriate urls are then fetched and parsed in order to find all the ``<img>`` tags available as *vac* and *vắc*. 
