import numpy as np

def point_velocity(blobs,NEWEXC,outline):
    """centered cross correlation of two time series

    Parameters
    ----------
    NEWEXC : np.array((T,X,Y),dtype=bool)
        new excitation mask
    outline : np.array((X,Y),dtype=bool)
        mask of pixels in embryo

    Returns
    --------
    speed : (# evenly spaced points along contour,)
        distance from point to edge of new excitation regions
    speedmsk : np.array((T,X,Y),dtype=np.float32)
        pixel value represents amplitude of edge propagation. pixels outside of embryo are labeled -1
    """

    imshape = NEWEXC.shape
    ampstk = np.full(imshape,-1,dtype=np.float32)
    from skimage.morphology import binary_erosion,disk
    outline = binary_erosion(outline, disk(10))
    blobzs = list(blobs.keys())
    speed = []
    for pz in np.arange(blobzs[0],blobzs[-1]):
        if pz not in blobs.keys() or pz+1 not in blobs.keys():
            continue
        for b in blobs[pz][::5]:
            b.sparseContour()
            for point in b.points:
                x,y = point['xy']                
                if not outline[x,y]:
                    amp = None
                    continue
                
                if NEWEXC[pz,x,y]:
                    lineim = line_intensity(point['xy'],point['uv'],NEWEXC[pz+1])
                    amp = count11(lineim)
                else:
                    amp = None
                point['amp'] = amp
                if amp is not None:
                    speed.append(amp)
                    x,y = rect_zxy(point,imshape[1:])
                    ampstk[pz,x,y] = amp
    return np.array(speed), ampstk

def line_intensity(pointxy,pointuv,im,maxlength=20):
    """intensity of pixels along the line that start front pointxy in the direction of pointuv

    Parameters
    ----------
    pointxy : np.array((2,),dtype=int)
        x,y coordinates of point
    pointuv : np.array((2,),dtype=int)
        u,v coordinates of point
    im : np.array((X,Y),dtype=bool)
        single frame of new excitation image
    maxlength : int
        maximum length of the line

    Returns
    --------
    lineim : np.array((N,),dtype=bool)
        intensity of pixels along the line sorted by distance to the startxy in ascending order
    """

    # draw a line with length "maxlength" from point in the direction of its outward pointing vector
    xystart,xyend = pointxy,(pointxy+pointuv*maxlength).astype(int)
    from skimage.draw import line
    linex,liney = line(*xystart,*xyend)#[1:]
    # remove pixels outside of either x bounds or y bounds
    m = np.stack([linex>=0,linex<im.shape[1],liney>=0,liney<im.shape[0]],-1)
    m = np.all(m,-1)
    if m.sum()<2:# ignore lines drawn near xy bounds
        return
    lineim = im[linex[m],liney[m]]# intensity of pixels along the line
    return lineim
        
def count11(seq):
    """count the lenghth of first consecutive '1's in binary sequence

    Parameters
    ----------
    seq : np.array((N,),dtype=bool)
        binary time series

    Returns
    --------
    length : int
        lenghth of first consecutive '1's
    """

    if not seq[1]:#no new excitation neighboring the point
        return 0

    start = 0
    while not seq[start]:
        start += 1
        if not start<len(seq):
            break
    if start>=len(seq)-1:
        return int(seq[-1])
    end = start
    while seq[end]:
        end += 1
        if not end<len(seq):
            break
    return end-start

def rect_zxy(p,imshape,L=(0,5),W=3):
    """find pixels in the bounding rectangle of a vector

    Parameters
    ----------
    p : dict
        vector {'xy':xy,'uv':uv}
    imshape : tuple
        dimensions of image (X,Y)
    L : tuple
        relative start and end points of the rectangle along the vector
    W : int
        dimention of rectangle perpendicular to the vector

    Returns
    --------
    rectx : np.array((N,),dtype=int)
        x coordinate of pixels in rectangle
    recty : np.array((N,),dtype=int)
        y coordinate of pixels in rectangle
    """

    vec = [p['xy']+p['uv']*L[0],p['xy']+p['uv']*L[1]]
    poly = rectangle(*vec,W)
    from skimage.draw import polygon
    rectx,recty = polygon(*poly.T, shape=imshape)
    return rectx,recty

def rectangle(p,q,W):
    """locate the x,y coordinates of the bounding rectangle of a vector

    Parameters
    ----------
    p : int
        start point of vector
    q : int
        end point of vector

    Returns
    --------
    length : int
        lenghth of first consecutive '1's
    """

    vpq = q-p
    v = np.flip(vpq)*np.array([-1,1])
    vnorm = np.linalg.norm(v)
    v = v/vnorm*W
    poly = (p+v,p-v,q-v,q+v)
    poly = np.round(np.vstack(poly)).astype(int)
    return poly


