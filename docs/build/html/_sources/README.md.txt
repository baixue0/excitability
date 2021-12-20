# Quantification of the spatiotemporal excitation patterns

This is a guide on how to reproduce the crucial plots and movies in the paper xxx.

## Data organization

### Raw tiff image stacks and table of all embryos
During image acquisition, each embryo is given an unique ID made up of the date and acquisition order. The acquired image is a 16-bit TIFF image stack whose stack position is the relative acquisition time in the timelapse video and is stored at `data/tiff_ROK/phenotype/ID/ID_channel.tif`. The ID, genotype, genetic perturbation and imaging conditions of each embryo is written as one row in the table and saved as CSV format. The table is loaded as a pandas Dataframe in python, which simplifies the selection and grouping of embryos based on its field (column) values. For example, 
```python
embryos['note'].str.startswith('SD')
``` 
selects the embryos imaged using spinning disk (SD) microscopy, where “embryos” is the Dataframe and its field ‘note’ contains information about imaging conditions. I also used the comment feature of CSV format to exclude embryos and to write a note to my future self.

### Label pixels in the embryo
To visualize the location of the embryo, the maxium projection of the first 100 frames of the raw image stack is stored at `data/tiff_outline/ID.tif` and then opened in ImageJ. The polygon or freehand tool in ImageJ is used to draw lines at the edge of the embryo. The resulting drawing is then converted to a binary mask and saved at `data/tiff_outline/poly-ID.tif`. 

### Label pulsing regions in the embryo


{% comment %} 
    These commments will not include inside the source.
manually labeled the binary mask that defines the pixels inside of the embryo, and points located in pulsing regions with different amplitudes. The binary mask of embryo outline is saved as a tiff file and imported in python as a boolean numpy array. The pulsing regions are saved as multipoint ROI (region of interest) and imported in python as objects containing the stack positions and spatial coordinates of each labeled point.
Aggregate manually labeled pulsing regions to determine the threshold for embryos of the same phenotype
Read ROIs and measure temporal derivative of ROK for each labeled region
Organize output data
decorator
Plot summary statistics




This iterative process of refining the segmentation workflow and imaging conditions is time consuming but rewarding. 


The second section shows the steps to process each embryo, from the raw images to summary statistics. During this process, individual embryos are processed independently at most steps, but a few steps require the aggregate information from multiple embryos. The complete workflow is shown in section three. At the end of the workflow, the summary statistics from embryos of the same phenotype are aggregated and plotted as histograms.


What did you learn?
What makes your project stand out?
If your project has a lot of features, consider adding a "Features" section and listing them here.


What was your motivation?
Why did you build this project?

{% endcomment %}