# Getting started

This is a guide on how to perform the analysis and reproduce the crucial plots and movies in the paper xxx. 

The systemic view of source code and documentation can be accessed {doc}`HERE <generated/src>`

## Data organization

### Raw tiff image stacks and table of all embryos
During image acquisition, each embryo is given an unique ID made up of the date and acquisition order. The acquired image is a 16-bit TIFF image stack. The stack position is the relative acquisition time in the timelapse video and is stored at `data/tiff_ROK/phenotype/ID/ID_channel.tif`. The ID, genotype, genetic perturbation and imaging conditions of each embryo is written as one row in the table and saved as CSV format. The table is loaded as a pandas `Dataframe` in python, which simplifies the selection and grouping of embryos based on its field (column) values. 

To read the table of embryo information, run
```python
import pandas as pd
embryos = pd.read_csv(pjoin([dir_data,'embryos.csv']),skipinitialspace=True,comment='#').set_index('ID')
``` 

Pandas also make it easy to group embryos by their phenotypes and apply a function to each phenotype group. In the example below, `lambda` is applied to each phenotype group; `func` is applied to every embryo within a given phenotype group; `vstack` aggregates the returned value from `func` for all embryos within the phenotype group.
```python
groups = embryos.groupby('phenotype')
# group.index is a list of embryo IDs whose phenotypes are the same
groups.apply(lambda group: np.vstack([func(ID) for ID in group.index]))
``` 
The code to select embryos based on their field value is `selectEmbryo` {doc}`LINK <generated/src.scripts.quant>`

### Label pixels in the embryo
The maxium projection of the first 100 frames of the raw image stack is stored at `data/tiff_outline/ID.tif`. In ImageJ, I opened the previous image and label the boundaries of the embryo using the polygon or freehand tool. The resulting drawing is then converted to a binary mask and saved at `data/tiff_outline/poly-ID.tif`. 

To read and save images or image stacks, run
```python
from skimage import io
io.imread(path_to_image)
# common data types include np.float32, np.uint8, np.uint16. 
# np.float64 images can not be opened by ImageJ
import tifffile
tifffile.imsave(path_to_image,np_array.astype(np.uint16))
``` 

### Label pulsing regions in the embryo
In ImageJ, I opened the raw image stack and labeled pulsing regions with the multipoint selection tool. The labeled points are added to ROI Manager and saved at `data/tiff_ROK_manual_circles/phenotype-ID.zip`. The code to read saved ROIs is `read_roi_zip` {doc}`LINK <generated/src.measure.read_roi>`. 

### Return function output as dictionaries
`return_dict` {doc}`LINK <generated/src.utils.decorators>` converts the tuple of variables returned by `func` to a dictionary `variable_name:variable_value`. To save the dictionary as an `ID.npy` file, `func` needs to return a list of strings `savedir`, which used to construct the save directory. `return_dict` modifies `savedir` so that the folder containing `ID.npy` is given the same name as `func`.

### Apply the same function to a list of embryos
`iterate` {doc}`LINK <generated/src.utils.decorators>` serves the same function as a for loop with added functionalities. Applying `func` to all embryos returns `{ID:func(phenotype,ID,*args,**kwargs)}`. `args` and `kwargs` allows one to pass an unspecified number of arguments to `func`. If `func(phenotype,ID,*args,**kwargs)` returns `None`, this `ID` will not be added to the dictionary returned by `iterate`. `iterate` prints the embryo to be analyzed in real time, so if `func` fails on one specific embryo, the same exception can be reproduced for debugging. To randomize the order of execution, set `shuffle=True`. Shuffling speeds up debugging because the embryos are organized by phenotype and `func` tested using one phenotype are more likely to fail on a different phenotype.

## Code organization
The code is made up of python source code `src` and the MarkDown or reStructuredText code `docs`

### python code `src`
`src` contains two types of modules. Python scripts in the `scripts` module are executed by shell commands. Functions and classes in other modules, ({doc}`measure <generated/src.measure>`,{doc}`utils <generated/src.utils>`,{doc}`visualization <generated/src.visualization>`,{doc}`simrd <generated/src.simrd>`), are used by scripts either directly or indirectly. Click on each module to see documentations and source codes of it submodules.

### documentation code `docs`
`docs` contains code to document `src` automatically using [sphinx](https://www.sphinx-doc.org/en/master/). Click {doc}`sphinx <sphinx>` to see how to generate documentation from python docstring. 

### FileTree
```
   [excitability]
   ├──__int__.py
   ├──[docs]
   │   ├──.nojekyll
   │   ├──Makefile
   │   ├──README.md
   │   ├──index.html
   │   ├──make.bat
   │   ├──requirements.txt
   │   └──[source]
   │       ├──FileTreeMaker.py
   │       ├──README.md
   │       ├──conf.py
   │       ├──index.rst
   │       ├──pyenv.rst
   │       └──sphinx.rst
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
```
To generate FileTree, run
```console
cd excitability/docs/source
python -u source/FileTreeMaker.py -r ../../excitability -xf env -xn .pyc .ipynb_checkpoints .ipynb .DS_Store __pycache__ build generated .git
```
