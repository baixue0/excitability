import numpy as np

def findContours(exc):
    """detect contour of connected pixels

    See more at :class:`src.measure.contour.Blob`

    Parameters
    ----------
    stk : `numpy.ndarray`, (T_raw,X,Y), np.float32
        raw image stack

    Returns
    --------
    blobs : dict
        dictionary of a list of blobs in each frame. ``{frame0:[blob0, ...], frame1:[blob0, ...], ...}``. 
    """

    import cv2
    exc[:,0,:] = False
    exc[:,-1,:] = False
    exc[:,:,0] = False
    exc[:,:,-1] = False

    nzzs = np.where(exc.max(1).max(1))[0]
    bs = {i:[] for i in nzzs}# {pz:[b0,b1,...],pz+1:[...], ...}
    for pz in nzzs:
        im = exc[pz].astype(np.uint8)
        numLabels, labels, stats, centroids = cv2.connectedComponentsWithStats(im, 8)
        for label in range(1,numLabels):
            area = stats[label, cv2.CC_STAT_AREA]
            m = labels==label
            pixels = np.stack(np.where(m),-1)
            cnt = np.fliplr(np.squeeze(cv2.findContours(m.astype(np.uint8),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)[0]))
            b = Blob(pixels,cnt,pz,len(bs[pz]))
            bs[pz].append(b)
    return bs
        

class Blob(object):
    """
    one excitation region

    Attributes
    ----------
    pixels : ndarray, (N,2)
        x,y cordinates of pixels within the excitation region
    pixelsp : list of tuples, [(x0,y0),(x1,y1), ...]
        same as pixels
    cnt : ndarray, (N,2)
        x,y coordinates of pixels along the boundary of the excitation region
    cntp : list of tuples, [(x0,y0),(x1,y1), ...]
        same as cnt
    pz : int
        frame number
    j : int
        index of blob in frame pz
    points : list of dict, ``[{'xy':xy1,'uv':uv1}, {'xy':xy2,'uv':uv2}, ...]``
        the x,y coordinates and unit bisector vector of one boundary point is saved in one dict
    """

    def __init__(self,pixels,cnt,pz,j):
        self.pixels = pixels
        self.pixelsp = [(x,y) for x,y in pixels]# location of pixels inside of blob[(x0,y0),(x1,y1), ...]
        self.cnt = cnt
        self.cntp = [(x,y) for x,y in cnt]# location of pixels along the edge of blob [(x0,y0),(x1,y1), ...]
        self.pz = pz
        self.j = j
        
    def sparseContour(self,N=5):# [(x0,y0),(x1,y1),...]
        """find evently spaced points along the contour and the outward facing bisector at each point

        add a list of dictionaries which contains the xy position and unit bisector vector

        Parameters
        ----------
        N : int
            the distance between neighboring points

        """

        cntp = self.cntp
        
        i0,i1 = 0,1# i0 points to the left of a segment with lenght N, i1 points to the right
        cntp2 = [cntp[i0]]
        while i1<len(cntp):
            while i1<len(cntp) and np.linalg.norm([[cntp[i0][0]-cntp[i1][0]],[cntp[i0][1]-cntp[i1][1]]])<N:
                i1 += 1# i1 move right until reaching the right end or the distance between i0 and i1 point is less than N
            if i1==len(cntp):
                break
            if np.linalg.norm([[cntp2[0][0]-cntp[i1][0]],[cntp2[0][1]-cntp[i1][1]]])<N/2:# stop when distance between i1 point and the left most point is less than N/2
                break
            cntp2.append(cntp[i1])
            i0 = i1
            i1 += 1
        sparsexy = np.stack(cntp2,axis=0).astype(int)

        # vectors connecting neighoring two sparse points along contour
        uv = np.vstack([np.diff(sparsexy,axis=0),sparsexy[0]-sparsexy[-1]])#uv[i-1] points towards i, uv[i] points away from i
        uv = uv/np.expand_dims(np.linalg.norm(uv,axis=1),1)
        
        # outward facing bisector vectors at sparse points
        sparseuv = np.zeros(uv.shape)
        for i in range(uv.shape[0]):
            sparseuv[i] = uv[i-1]-uv[i]# sparseuv[i] bisecs edges centered at i
        for i in np.where(np.linalg.norm(sparseuv,axis=1)==0)[0]:# special case: two vectors parallel
            sparseuv[i] = np.flip(uv[i])*np.array([1,-1])# rotate parallel vector by 90 degrees
        sparseuv = sparseuv/np.expand_dims(np.linalg.norm(sparseuv,axis=1),1)# bisector of two given vector
        from skimage.measure import points_in_poly
        concave = points_in_poly(sparsexy+sparseuv*0.1, sparsexy)# invert inward pointing vectors
        sparseuv[concave] *= -1

        self.points = [{'xy':sparsexy[i],'uv':sparseuv[i]} for i in range(len(sparsexy))]
        
