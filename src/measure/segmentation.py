from utils import return_dict
import numpy as np

@return_dict
def excitation(savedir,DIFF,outline,THRESH):
    """pixels in DIFF above THRESH is EXC; the first frame to cross the threshold is NEWEXC

    Parameters
    ----------
    savedir : str
        path to save returned values
    DIFF : `numpy.ndarray`, (T,X,Y), np.float32
        temporal difference
    outline : `numpy.ndarray`, (X,Y), bool
        mask of pixels in embryo
    THRESH : float
        threshold value

    Returns
    --------
    savedir : str
        path to save returned values
    EXC : `numpy.ndarray`, (T,X,Y), bool
        excitation mask
    NEWEXC : `numpy.ndarray`, (T,X,Y), bool
        new excitation mask
    outline : `numpy.ndarray`, (X,Y), bool
        mask of pixels in embryo
    """

    EXC = DIFF>THRESH
    EXC[:,~outline] = False

    nzzs = nonzeroz(EXC)
    from skimage.morphology import remove_small_objects
    for z in nzzs:
        EXC[z] = remove_small_objects(EXC[z], min_size=10**2)
        
    NEWEXC = np.zeros(EXC.shape,bool)
    NEWEXC[nzzs[1:]] = np.diff(EXC[nzzs].astype(int),axis=0)>0
    
    return savedir,EXC,NEWEXC,outline

@return_dict
def group_diff(stk,outline,tRes):
    """group imagestack; smooth in space and time

    Parameters
    ----------
    stk : `numpy.ndarray`, (T_raw,X,Y), np.float32
        raw image stack
    outline : `numpy.ndarray`, (X,Y), bool
        mask of pixels in embryo
    tRes : float
        time between consecutive frames

    Returns
    --------
    RAW : `numpy.ndarray`, (T,X,Y), np.uint16
        raw
    SMOOTH : `numpy.ndarray`, (T,X,Y), np.float32
        smoothed
    DIFF : `numpy.ndarray`, (T,X,Y), np.float32
        temporal difference 
    zgroups : nested 1D array
        frames that are grouped together
    """

    N = len(stk)
    groupsize = int(1.2 // tRes)# group consecutive frames so that each group is 1.2 sconds
    RAW,zgroups = grouped_avg(stk,groupsize)
    RAW = RAW.astype(np.uint16)

    smooth = np.stack([smoothxy(stk[z].copy().astype(np.float32)) for z in range(N)],0)
    smooth = moving_avg(smooth,groupsize).astype(np.float32)
    SMOOTH,zgroups = grouped_avg(smooth,groupsize)
    DIFF = diff(SMOOTH,outline).astype(np.float32)
    return RAW,SMOOTH,DIFF,zgroups


def bleach_correction(stk, outline, window_length, videozmin):
    """compensate for photobleach

    Parameters
    ----------
    stk : `numpy.ndarray`, (T_raw,X,Y), np.float32
        raw image stack
    outline : `numpy.ndarray`, (X,Y), bool
        mask of pixels in embryo
    window_length : int
        window_length for savgol_filter smoothing
    videozmin : int
        mask of pixels in embryo

    Returns
    --------
    y : 1D array
        average intensity of all pixels in embryo at each time point
    ys : 1D array
        smooth y with savgol_filter
    imbc : `numpy.ndarray`, (T_raw,X,Y), np.float32
        image stack after compensating for photobleach
    """

    outlier_bounds = lambda arr: (np.percentile(arr,10**-4),np.percentile(arr,100-10**-4))
    stk = np.clip(stk,*outlier_bounds(pixelsinembryo(stk, outline)))
    from scipy.signal import savgol_filter
    y = pixelsinembryo(stk, outline).mean(1)
    ys = savgol_filter(y, window_length=window_length, polyorder=1)# smooth signal
    compensation = (ys[:videozmin].mean()-ys)[:,None,None]
    imbc = (stk+compensation).astype(np.uint16)
    return y,ys,imbc

def diff(stk,outline,window=2):
    """temporal derivative with given window size of 4.8 seconds

    Parameters
    ----------
    stk : `numpy.ndarray`, (T_raw,X,Y), np.float32
        raw image stack
    outline : `numpy.ndarray`, (X,Y), bool
        mask of pixels in embryo
    window : int, optional
        window_length for savgol_filter smoothing

    Returns
    --------
    diff_normed : `numpy.ndarray`, (T,X,Y), np.float32
        image stack after compensating for photobleach
    """
    
    nzzs = nonzeroz(stk)
    diff = np.zeros(stk.shape,dtype=np.float32)# temporal derivative image
    for z in nzzs[window:-window]:#skip the first and last few frames where pixels are all zero
        diff[z] = stk[z+window]-stk[z-window]# time window for difference is 4*1.2 seconds
    temp = pixelsinembryo(diff, outline)
    diff_normed = (diff-temp.mean())/temp.std()
    return diff_normed

def smoothxy(im):
    '''
    apply filters to smooth image in space
    '''
    import cv2
    im = cv2.medianBlur(im, 5)
    im = cv2.medianBlur(im, 5)
    im = cv2.GaussianBlur(im,(19,19),0)
    return im

def moving_avg(stk,groupsize):
    '''
    centered moving average
    the stack positions at the first and last groupsize frames defaults to zero
    '''
    out = np.zeros(stk.shape,dtype=stk.dtype)
    for i in np.arange(groupsize,stk.shape[0]-groupsize):
        out[i] = stk[i-groupsize:i+groupsize].mean(0)
    return out

def grouped_avg(stk,groupsize):
    '''
    return the average of each group
    '''
    N = stk.shape[0]
    zgroupmax = int(np.floor(N/groupsize))*groupsize
    zgroups = np.split(np.arange(zgroupmax),np.arange(groupsize,zgroupmax,groupsize))
    return np.stack([stk[z].mean(0) for z in zgroups],0).astype(stk.dtype),zgroups

def pixelsinembryo(stk, outline):
    outlinex,outliney = np.where(outline)
    return stk[:,outlinex,outliney]

nonzeroz = lambda stk:np.where(stk.max(1).max(1))[0]
