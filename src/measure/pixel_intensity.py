import numpy as np

def ccfbf(ts,ts2):
    """centered cross correlation of two time series

    Parameters
    ----------
    ts : `numpy.ndarray`, (T,)
        first time series
    ts2 : `numpy.ndarray`, (T,)
        second time series

    Returns
    --------
    crosscorr : (2T-1,)
        centered cross correlation
    """
    
    from statsmodels.tsa.stattools import ccf
    backwards = ccf(ts[::-1], ts2[::-1], adjusted=False)[::-1]
    forwards = ccf(ts, ts2, adjusted=False)
    return np.r_[backwards[:-1], forwards]

def ts_embryo(imstkgr,NEWEXC,speedmsk,NMAX=100):
    outline = imstkgr['outline']
    dz=np.arange(-5,6)
    result = {'dz':dz}
    channel = 'img'
    result['_'.join(['newexc',channel,'raw'])] = intensity_ts(NEWEXC[:NMAX],imstkgr[channel]['RAW'][:NMAX],dz,outline)
    
    ccf_col = lambda ts,ts2: np.stack([ccfbf(ts[:,pixel], ts2[:,pixel]) for pixel in np.arange(ts.shape[1])],0)
    
    cx,cy = np.stack(np.where(outline),-1).mean(0).astype(int)
    dxy = 40
    grect = imstkgr[channel]['SMOOTH'][1:NMAX-1,cx-dxy:cx+dxy,cy-dxy:cy+dxy].mean(-1).mean(-1)[:,np.newaxis]
    result['_'.join(['acfrect','smooth'])] = ccf_col(grect,grect)

    g = imstkgr[channel]['SMOOTH'][1:NMAX-1,outline]
    result['_'.join(['acf','smooth'])] = ccf_col(g,g)
    
    channel = 'imr'
    if channel not in imstkgr.keys():
        return result

    result['_'.join(['newexc',channel,'raw'])] = intensity_ts(NEWEXC[:NMAX],imstkgr[channel]['RAW'][:NMAX],dz,outline)
    result['_'.join(['newexc',channel,'diff'])] = intensity_ts(NEWEXC[:NMAX],imstkgr[channel]['DIFF'][:NMAX],dz,outline)
    result['_'.join(['fast',channel,'diff'])] = intensity_ts((speedmsk>2)[:NMAX],imstkgr[channel]['DIFF'][:NMAX],dz,outline)
    result['_'.join(['slow',channel,'diff'])] = intensity_ts(np.logical_and(speedmsk>=0, speedmsk<=2)[:NMAX],imstkgr[channel]['DIFF'][:NMAX],dz,outline)

    r = imstkgr[channel]['SMOOTH'][1:NMAX-1,outline]
    result['_'.join(['ccf','smooth'])] = ccf_col(g,r)
    
    for name in result.keys():
        print(name,result[name].shape)
    return result


def roi_to_stkmask(imshape,zgroups,path_circles):
    """read multipoint ROIs; converts to binary mask where ROI is True

    Parameters
    ----------
    imshape : tuple
        (T,X,Y)
    zgroups : nested 1D array
        frames that are grouped together
    path_circles : str
        path to ROIs

    Returns
    --------
    msk : `numpy.ndarray`, (T,X,Y), bool
        binary mask where ROI is True
    """
    msk = np.zeros(imshape,dtype=bool)
    zgroups = np.stack(zgroups,0)
    from measure.read_roi import read_roi_zip
    for p in read_roi_zip(path_circles).values():
        z,x,y = p['position'],p['y'][0],p['x'][0]# z is maunally labeled before grouped average, need to find z after grouping
        found = np.where(zgroups==z)[0]
        if len(found)==1:
            msk[int(found[0]),int(x),int(y)] = True
    return msk

def intensity_ts(msk,measure,dz,outline):
    """read multipoint ROIs; converts to binary mask where ROI is True

    Parameters
    ----------
    msk : `numpy.ndarray`, (T,X,Y), bool
        pixels to measure
    measure : `numpy.ndarray`, (T,X,Y)
        intensity image stack
    dz : `numpy.ndarray`, (DT,), int
        time offset to measure intensity
    outline : `numpy.ndarray`, (X,Y), bool
        mask of pixels in embryo

    Returns
    --------
    ts : `numpy.ndarray`, (DT,#pixels in msk)
        intensity at different time offsets
    """

    msk[:,~outline] = False
    if msk.sum()==0:
        print('all False in binary mask')
        return
    zmax = measure.shape[0]
    nzzs = np.where(msk.max(1).max(1))[0]# non zero z positions
    zs = nzzs[np.logical_and(nzzs+dz[0]>=0,nzzs+dz[-1]<zmax)]
    if len(zs)==0:
        print('binary mask out of measure stack')
        return
    result  = np.vstack([(measure[z+dz][:,msk[z]]).T for z in zs])
    return result



