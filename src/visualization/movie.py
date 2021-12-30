'''
functions to make movies
'''
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

def create_title(imshape,txt,heightratio=0.2,textcolor=(0,0,0)):
    import cv2
    height = int(imshape[1]*heightratio)
    titleim = np.full((height,imshape[2]), 255, dtype=np.uint8)
    #coordinates of the bottom-left corner of the text string in the image
    x,y = int(imshape[1]*0.3),int(height*0.7)
    cv2.putText(titleim, txt, org=(x,y), fontFace=cv2.FONT_HERSHEY_SIMPLEX , fontScale=1, color=textcolor, thickness=2)
    titlestk = np.stack([np.stack([titleim]*imshape[0],0)]*3,-1)
    return titlestk

def time_scalebar(stk,dt,cbarstk=None,textcolor=(0,0,0),padcolor=(255,255,255)):
    """overlay time stamp and scale bar on image stack

    Parameters
    ----------
    im : np.array((T,X,Y,3),dtype=np.uint8)
        original image stack
    dt : float
        time gap between consecutive frames
    cbarstk : list of np.array((X,Y,3),dtype=np.uint8)
        image stack of colorbar

    Returns
    --------
    labeled : np.array((T,X,Y,3),dtype=np.uint8)
        labeled image stack

    """

    imshape = stk.shape
    timex,timey = int(imshape[1]*0.06),int(imshape[1]*0.13)
    scalex,scaley = int(imshape[1]*0.05),int(imshape[1]*0.95)
    import cv2
    for i in range(imshape[0]):
        cv2.putText(stk[i], str(round(dt*i,1))+' S', org=(timex,timey), fontFace=cv2.FONT_HERSHEY_SIMPLEX , fontScale=1, color=textcolor, thickness=2)#label time at top left corner
        cv2.line(stk[i], pt1=(scalex,scaley), pt2=(scalex+50,scaley), color=textcolor, thickness=2)# scale bar 5um at bottom left corner
    if cbarstk is not None:
        stk = np.dstack([np.hstack(cbarstk),stk])#stack left to right
    return stk

def boarder(im,top_bottom_left_right,padcolor=[0,0,0]):#input RGB 8bit image
    """add boarder to image or imagestack

    Parameters
    ----------
    im : np.array((X,Y,3),dtype=np.uint8) or (T,X,Y,3)
        original image stack
    top_bottom_left_right : tuple of int
        top, bottom, left, right

    Returns
    --------
    resized : np.array((top+X+bottom,left+Y+right,3),dtype=np.uint8) or (T,top+X+bottom,left+Y+right,3)
        resized image stack

    """

    import cv2
    if im.ndim==3:
        return cv2.copyMakeBorder(im, *top_bottom_left_right, cv2.BORDER_CONSTANT, None, padcolor)#top, bottom, left, right
    elif im.ndim==4:
        return np.stack([cv2.copyMakeBorder(im[i], *top_bottom_left_right, cv2.BORDER_CONSTANT, None, padcolor) for i in range(im.shape[0])],0)

def stk_upsizexy(imstk,scale=4):
    """resize imagestack

    Parameters
    ----------
    imstk : np.array((T,X,Y),dtype=np.uint8) or (T,X,Y,3)
        original image stack
    scale : float
        percent of original x,y dimension

    Returns
    --------
    resized : np.array((T,X*scale,Y*scale),dtype=np.uint8) or (T,X*scale,Y*scale,3)
        resized image stack
        
    """

    import cv2
     # percent of original size
    width = int(imstk.shape[2] * scale)
    height = int(imstk.shape[1] * scale)

    result = []
    for z in range(imstk.shape[0]):
        upsized = cv2.resize(imstk[z], (width, height), interpolation = cv2.INTER_AREA)
        result.append(upsized)
    return np.stack(result)

def saveMP4(path,imtsk,fps):
    """save imagestack as MP4 file with `imageio <https://pypi.org/project/imageio/>`_
    
    Parameters
    ----------
    path : str
        path to save MP4
    imtsk : np.array((T,X,Y,3),dtype=np.uint8)
        image stack to convert
    fps : int
        frames per second

    """

    import imageio
    writer = imageio.get_writer(path+'.mp4', fps=fps)
    for im in imtsk:
        writer.append_data(im)
    writer.close()

def rotate(path,stk):
    from measure.preprocess import read_outline
    outline = read_outline(path)
    from visualization.rotate_crop import Rotate_Crop
    RC = Rotate_Crop(outline)
    stk[:,~outline] = 255
    stk = RC.rotate_stk(stk,255)
    return stk

