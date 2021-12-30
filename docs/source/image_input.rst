Input
--------

raw tiff image stacks and table of all embryos
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

During image acquisition, each embryo is given an unique ID made up of the date and acquisition order. 

The acquired image is a 16-bit TIFF image stack. The stack position is the relative acquisition time in the timelapse video and is stored at *data/tiff_ROK/phenotype/ID/ID_channel.tif* 

The ID, genotype, genetic perturbation and imaging conditions of each embryo is written as one row in the table and saved as CSV format. The table is loaded as a pandas **Dataframe** in python, which simplifies the selection and grouping of embryos based on its field (column) values. 

The following example reads the CSV file and set embryo ID as the index. ``skipinitialspace`` Skip spaces after delimiter. By setting ``comment='#'`` , comments can be added to the CSV file to annotate each embryo. 

.. code-block:: python

    import pandas as pd
    embryos = pd.read_csv(path_to_csv,skipinitialspace=True,comment='#').set_index('ID')


Pandas also make it easy to group embryos by their phenotypes and apply a function to each phenotype group. In the example below, **lambda** is applied to each phenotype group; **func** is applied to every embryo within a given phenotype group; **vstack** aggregates the returned value from **func** for all embryos within the phenotype group.

.. code-block:: python

    groups = embryos.groupby('phenotype')
    # group.index is a list of embryo IDs whose phenotypes are the same
    groups.apply(lambda group: np.vstack([func(ID) for ID in group.index]))


label pixels in the embryo
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In ImageJ, I opened the maxium projection of the first 100 frames of the raw image stack (*data/tiff_outline/ID.tif*) and drew the boundaries of the embryo using the polygon or freehand tool. The resulting drawing is then converted to a binary mask and saved at *data/tiff_outline/poly-ID.tif* 

To read images or image stacks

.. code-block:: python

    from skimage import io
    image = io.imread(path_to_image)

To save image (stacks), the numpy array representing the image (stacks) need to be converted to one of the following data types: np.float32, np.uint8, np.uint16. When saving image stacks, the array needs to be converted to shape (T,X,Y) to be read by ImageJ as image stack.

.. code-block:: python

    import tifffile
    tifffile.imsave(path_to_image, array.astype(np.uint16)) 

label pulsing regions in the embryo
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In ImageJ, I opened the raw image stack and labeled pulsing regions with the multipoint selection tool. The labeled points are added to ROI Manager and saved at *data/tiff_ROK_manual_circles/phenotype-ID.zip*. The code to read saved ROIs is :func:`src.measure.read_roi.read_roi_zip`. 

