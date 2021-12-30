import numpy as np


from numba import njit
@njit
def index_first_true(arr):
    """find the index of first True in a binary 1D array

    Parameters
    ----------
    arr : `numpy.ndarray`, (N,), bool
        array to search
    Returns
    --------
    index : int or None
        index of first True. If not found, return None
    """

    for idx, val in np.ndenumerate(arr):
        if val:
            return idx[0]

def frequency(stk,outline,example=False):
    """number of new excitations for each pixel

    Parameters
    ----------
    stk : `numpy.ndarray`, (T_raw,X,Y), np.float32
        raw image stack
    outline : `numpy.ndarray`, (X,Y), bool
        mask of pixels in embryo
    example : bool
        whether the returned value are used as example embryo

    Returns
    --------
    freq : `numpy.ndarray`, (# pixels in embryo), int
        number of new excitations for pixels in embryo

    Note
    --------
    returns the following when ``example==True``

    * freq : `numpy.ndarray`, (X,Y), int
        number of new excitations for all pixels. pixels outside of embryo are -1.

    """

    freq = stk.sum(0).astype(int)
    freq[~outline] = -1
    if not example:
        return freq[outline]
    return freq
        

def waittime(stk,outline,windowlength,example=False):
    """number of frames before next new excitation for each new excitation pixel

    Parameters
    ----------
    stk : `numpy.ndarray`, (T_raw,X,Y), np.float32
        raw image stack
    outline : `numpy.ndarray`, (X,Y), bool
        mask of pixels in embryo
    windowlength : int
        number of frames within which to search for the next new excitation
    example : bool
        whether the returned value are used as example embryo

    Returns
    --------
    waittime : `numpy.ndarray`, (N,), int
        number of frames before next new excitation

        N = # new excitation pixels able to observe the entire window

    Note
    --------
    returns the following when ``example==True``

    * zxyr : `numpy.ndarray`, (N,3), int
        3 column : temporal coordinate, spatial coordinate, wait time
    * imshape : tuple, (T,X,Y), int
        used to reconstruct image stack

    """

    imshape = stk.shape
    stk[:,~outline] = False
    zxy = np.stack(np.where(stk),-1)#find z,x,y position of new excitation pixels
    zxyr = []
    for i,(z,x,y) in enumerate(zxy):
        ts = stk[z+1:min(z+windowlength,imshape[0]),x,y]
        r = index_first_true(ts)#find the next new excitation
        l = len(ts)
        if r is None:
            if l==windowlength-1:#no activation in observation window
                r = windowlength
            else:#unable to observe the entire window
                continue
        zxyr.append((z,x,y,r))
    zxyr = np.array(zxyr)
    if not example:
        return zxyr[:,-1]
    return zxyr, imshape
