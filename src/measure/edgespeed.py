import numpy as np

def point_velocity(blobs,NEWEXC,outline):
    '''
    find evenly spaced points along contour in new excitation regions at current frame; measure distance from point to edge of new excitation regions at next frame

    :returns: array of int
    '''
    imshape = NEWEXC.shape
    ampstk = np.full(imshape,-1,dtype=np.float32)
    from skimage.morphology import binary_erosion,disk
    outline = binary_erosion(outline, disk(10))
    blobzs = list(blobs.keys())
    amparr = []
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
                    amp = measure_amp(point['xy'],point['uv'],NEWEXC[pz+1])
                else:
                    amp = None
                point['amp'] = amp
                if amp is not None:
                    amparr.append(amp)
                    x,y = rect_zxy(point,imshape[1:])
                    ampstk[pz,x,y] = amp
    return np.array(amparr), ampstk

def measure_amp(pointxy,pointuv,im,maxlength=20):
    '''
    distance from point to edge of new excitation regions

    :returns: int
    '''
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
    if not lineim[1]:#no new excitation neighboring the point
        return 0
    return count11(lineim)
        
def count11(seq):
    '''
    count number of consecutive '1's in binary sequence

    :returns: int
    '''
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
    vec = [p['xy']+p['uv']*L[0],p['xy']+p['uv']*L[1]]
    poly = rectangle(*vec,W)
    from skimage.draw import polygon
    rectx,recty = polygon(*poly.T, shape=imshape)
    return rectx,recty

def rectangle(p,q,W):
    vpq = q-p
    v = np.flip(vpq)*np.array([-1,1])
    vnorm = np.linalg.norm(v)
    v = v/vnorm*W
    poly = (p+v,p-v,q-v,q+v)
    poly = np.round(np.vstack(poly)).astype(int)
    return poly


