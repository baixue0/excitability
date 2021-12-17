Project files and folders
---------------------------

Generate FileTree 
^^^^^^^^^^^^^^^^^^

go to directory ``~/Documents/GitHub/excitability/docs/source``

.. code-block:: console

    python -u FileTreeMaker.py -r ../../../excitability -xf env -xn .pyc .ipynb_checkpoints .ipynb .DS_Store __pycache__ build generated .git

FileTree 
^^^^^^^^^^^^^^^^^^

.. code-block:: none

   [excitability]
   ├──.readthedocs.yml
   ├──README.rst
   ├──__int__.py
   ├──[docs]
   │   ├──.nojekyll
   │   ├──Makefile
   │   ├──_config.yml
   │   ├──index.html
   │   ├──make.bat
   │   ├──requirements.txt
   │   └──[source]
   │       ├──FileTreeMaker.py
   │       ├──conf.py
   │       ├──index.rst
   │       ├──pyenv.rst
   │       ├──sphinx.rst
   │       └──structure.rst
   └──[src]
       ├──__int__.py
       ├──[measure]
       │   ├──__int__.py
       │   ├──contour.py
       │   ├──edgespeed.py
       │   ├──link.py
       │   ├──pixel_intensity.py
       │   ├──preprocess.py
       │   ├──read_roi.py
       │   ├──recurrence.py
       │   └──segmentation.py
       ├──[scripts]
       │   ├──__int__.py
       │   ├──movie123.py
       │   ├──movie456.py
       │   ├──quant.py
       │   ├──quant_plots.py
       │   └──sim.py
       ├──[simrd]
       │   ├──__int__.py
       │   ├──fitzhughnagumo.py
       │   └──srd.py
       ├──[utils]
       │   ├──__int__.py
       │   ├──decorators.py
       │   └──path_io.py
       └──[visualization]
           ├──__int__.py
           ├──fadingexc.py
           ├──image.py
           ├──movie.py
           ├──plot.py
           └──rotate_crop.py

