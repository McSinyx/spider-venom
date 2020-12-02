Scraping vaccine images from tuoitre
====================================

Site analysis
-------------

We scrape image and caption about vaccine from searched page from thanhnien.vn:

.. code-block:: html

   https://thanhnien.vn/vaccine

For the images and their captions in the articles, we will try to get the ``src``---image source and 
``alt``---image caption of the ``<img>`` tag. 

Scraping explanation
--------------------

The site taken is site for searched for vaccine in thanhnien.vn.

.. code-block:: python

   INDEX = 'https://thannien.vn/vaccine'
	
The scraper then focuses on 3 main functions articles(), scrape_image() and download() and one function
name thanhnien to run the function from main.py.

articles()
^^^^^^^^^^

.. code-block:: python
	
   def articles(links):
       """Find URLs contains 'vacxin' in the given link."""
       for a in links:
           href = a.get('href')
           if href is None: continue
           url = 'http://thanhnien.vn/' + href
           if url.endswith('.html') and 'vac' in url: yield url
		
From searched articles we focus only on url ended with html and vac in the url.

scrape_image()
^^^^^^^^^^^^^^

.. code-block:: python

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
				
The website used in vietnamese languages so we use both key words as *vac* and *vắc* for either *vaccine*
and *vắc xin*.

download()
^^^^^^^^^^

.. code-block:: python

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
	
The download function will download the image from ``src`` and the caption from ``alt``.
Each image and its caption is list on in folder and named ``image``, ``caption`` respectively inside a folder named by
the name of the website.
