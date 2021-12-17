import numpy as np


from numba import njit
@njit
def index_first_true(array):
    ''' 
    If no item was found return None, other return types might be a problem due to numbas type inference
    '''
    for idx, val in np.ndenumerate(array):
        if val:
            return idx[0]

def frequence(stk,outline,example=False):
    freq = stk.sum(0).astype(int)
    freq[~outline] = -1
    if not example:
        return freq[outline]
    return freq
        

def waittime(stk,outline,windowlength,example=False):
    '''
    find z,x,y position of new excitation pixels; in the following timeseries with length of windowlength, find the next new excitation.
    '''
    imshape = stk.shape
    stk[:,~outline] = False
    zxy = np.stack(np.where(stk),-1)
    zxyr = []
    for i,(z,x,y) in enumerate(zxy):
        ts = stk[z+1:min(z+windowlength,imshape[0]),x,y]
        r = index_first_true(ts)#
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
