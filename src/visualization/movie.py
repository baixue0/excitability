'''
help functions to make movies
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

def rotate(path,stk):
    from measure.preprocess import read_outline
    outline = read_outline(path)
    from visualization.rotate_crop import Rotate_Crop
    RC = Rotate_Crop(outline)
    stk[:,~outline] = 255
    stk = RC.rotate_stk(stk,255)
    return stk

def boarder(im,top_bottom_left_right,padcolor=[0,0,0]):#input RGB 8bit image
    import cv2
    if im.ndim==3:
        return cv2.copyMakeBorder(im, *top_bottom_left_right, cv2.BORDER_CONSTANT, None, padcolor)#top, bottom, left, right
    elif im.ndim==4:
        return np.stack([cv2.copyMakeBorder(im[i], *top_bottom_left_right, cv2.BORDER_CONSTANT, None, padcolor) for i in range(im.shape[0])],0)

def stk_upsizexy(imstk,scale=4):
    import cv2
     # percent of original size
    width = int(imstk.shape[2] * scale)
    height = int(imstk.shape[1] * scale)

    result = []
    for z in range(imstk.shape[0]):
        upsized = cv2.resize(imstk[z], (width, height), interpolation = cv2.INTER_AREA)
        result.append(upsized)
    return np.stack(result)

def saveMP4(path,images,fps):#https://imageio.readthedocs.io/en/stable/format_ffmpeg.html
    import imageio
    writer = imageio.get_writer(path+'.mp4', fps=fps)
    for im in images:
        writer.append_data(im)
    writer.close()
