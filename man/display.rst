Displaying the results
======================

After running::

   python -m spider man/venom

figures will be downloaded and stored inside ``man/venom`` folder. With each website-named folder, we can find the corresponding images and captions. 
E.g: Following the path ``venom/thanhnien/hiv-r-d1``, we will see an image file ``image.jpg`` and the caption named ``caption``. 
Then, as we include images and captions in these figures, through these function, we can provide html source as below::
 
   .. figure:: venom/thanhnien/hiv-r-d1/photo-1-16038675759312109833464/image.jpg

      .. include:: venom/thanhnien/hiv-r-d1/photo-1-16038675759312109833464/caption

Will provide html source code as::

   <div class="figure align-default" id="id1">
     <img alt="_images/image.jpg" src="_images/image.jpg" />
     <p class="caption"><span class="caption-text">...</span><a class="headerlink" href="#id1" title="Permalink to this image">¶</a></p>
   </div>
  
To do this, we will use::

   for image in iglob('venom/*/*/image.*'):
       results.write(FIGURE.format(image, join(dirname(image), 'caption')))


Where::

   FIGURE = """
   .. figure:: {}

      .. include:: {}

We will pick the image and caption inside the accessed folder for the figure. After that, we will make a formatted figure. Then when they are generated, they will be aligned and the caption will be joined underneath the image.

The results can be viewed on `the result page`__.

__ https://mcsinyx.github.io/spider-venom/results.html
