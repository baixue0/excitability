Image analysis
=================

Data and code organization
-------------------------------

.. image::  flow.jpg
   :width: 600 px

* The gray box shows the data and image processing for one embryo. 
* The texts and arrows represent data and image processing steps respectively. 
* Important image proceesing steps are labeled with circled numbers. 
* Input and output is labeled blue and green respectively. 
* Purple shows how the threshold is calculated from embryos of the same phenotype. Red texts indicate that they are the same data. Segmentation is broken into two steps because the threshold depends on ROK temporal derivative over time for all embryos of the same phenotype.

.. toctree::
   :maxdepth: 3

   image_embryo
   image_input
   image_output
   Example_jupyter_notebook
