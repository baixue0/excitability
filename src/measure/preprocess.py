from utils.path_io import pjoin,pexists
from utils.decorators import return_dict

@return_dict
def read_raw(savedir, dir_raw, ID, LabelR, tRes, nEnd):
    """read raw imagestack

    raw tif files are located in ``dir_raw``, start with ``ID``, and end with ``G`` or ``R``.

    refer to :func:`src.utils.decorators.return_dict` for how to use the decorator ``@return_dict``

    Parameters
    ----------
    savedir : list of str
        the directory to save the output as a dictionary

    dir_raw : str
        directory of raw tif files

    Returns
    -------
    savedir : list of str
        same as input savedir

    img : np.array((T,X,Y))
        cropped green channel image stack

    imr : np.array((T,X,Y))
        cropped red channel image stack

    """

    from skimage import io

    # find raw tif in embryo directory
    import os
    rawfname = lambda channel: [pjoin([dir_raw,fname]) for fname in os.listdir(dir_raw) if fname.startswith(ID) and fname.endswith(channel+'.tif')]
    
    # determine number of frames for 1.2 seconds
    groupsize = 1.2 // tRes

    # read
    img = io.imread(rawfname('G')[0])[2*groupsize:nEnd]# skip the first 2.4 seconds
    imr = None
    if not LabelR=='None':
        imr = io.imread(rawfname('R')[0])[2*groupsize:nEnd]

    return savedir, img, imr

def read_outline(fname_outline):
    """ read outline of embryo

    Returns
    -------
    outline : np.array((X,Y),dtype=bool)
        whether each pixel is in embryo 

    """

    if not pexists(fname_outline):
        return
    from skimage import io
    outline = io.imread(fname_outline)>0
    return outline


def channel_list(ID,embryos):
    """ helper function for :func:`src.scripts.quant.stepGroupDiff`

    Returns
    -------
    channels : list of str
        ``['img','imr']`` or ``['img']`` depending on whether the red channel is LifeAct

    """

    channels = ['img']
    if embryos.loc[ID]['LabelR']=='LA':
        channels.append('imr')
    return channels

