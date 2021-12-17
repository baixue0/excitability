from utils.path_io import pjoin,divide,pexists
from utils.decorators import return_dict

@return_dict
def read_raw(save, dir_raw, ID, LabelR, tRes, nEnd):
    '''
    read raw imagestack for both channels

    filename should startwith embryo ID and end with channel name 'G' or 'R'
    
    write time projection of green channel to outline directory
    '''
    from skimage import io

    # find raw tif in embryo directory
    import os
    rawfname = lambda channel: [pjoin([dir_raw,fname]) for fname in os.listdir(dir_raw) if fname.startswith(ID) and fname.endswith(channel+'.tif')]
    
    # determine number of frames for 1.2 seconds
    groupsize = divide(1.2,tRes)

    # read
    img = io.imread(rawfname('G')[0])[2*groupsize:nEnd]# skip the first 2.4 seconds
    imr = None
    if not LabelR=='None':
        imr = io.imread(rawfname('R')[0])[2*groupsize:nEnd]

    return save, img, imr

def read_outline(fname_outline):
    '''
    read outline of embryo
    '''
    if not pexists(fname_outline):
        return
    from skimage import io
    outline = io.imread(fname_outline)>0
    return outline


def channel_list(ID,embryos):
    '''
    if the red channel of embryo is LifeAct, return ['img','imr']
    else, return ['img']
    '''
    channels = ['img']
    if embryos.loc[ID]['LabelR']=='LA':
        channels.append('imr')
    return channels

