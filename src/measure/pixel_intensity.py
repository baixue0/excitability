import numpy as np

def ts_embryo(imstkgr,NEWEXC,speedmsk,NMAX=100):
    outline = imstkgr['outline']
    dz=np.arange(-15,6)
    result = {'dz':dz}
    channel = 'img'
    result['_'.join(['newexc',channel,'raw'])] = intensity_ts(NEWEXC[:NMAX],imstkgr[channel]['RAW'][:NMAX],dz,outline)
    
    from statsmodels.tsa.stattools import acf
    ts = imstkgr[channel]['SMOOTH'][1:-1,outline]
    result['_'.join(['acf',channel,'smooth'])] = np.stack([acf(ts[:,pixel], nlags=40) for pixel in np.arange(ts.shape[1])])
    ts = imstkgr[channel]['DIFF'][1:-1,outline]
    result['_'.join(['acf',channel,'diff'])] = np.stack([acf(ts[:,pixel], nlags=40) for pixel in np.arange(ts.shape[1])])
    
    channel = 'imr'
    if channel not in imstkgr.keys():
        return result
    result['_'.join(['newexc',channel,'raw'])] = intensity_ts(NEWEXC[:NMAX],imstkgr[channel]['RAW'][:NMAX],dz,outline)
    result['_'.join(['newexc',channel,'diff'])] = intensity_ts(NEWEXC[:NMAX],imstkgr[channel]['DIFF'][:NMAX],dz,outline)
    result['_'.join(['fast',channel,'diff'])] = intensity_ts((speedmsk>2)[:NMAX],imstkgr[channel]['DIFF'][:NMAX],dz,outline)
    result['_'.join(['slow',channel,'diff'])] = intensity_ts(np.logical_and(speedmsk>=0, speedmsk<=2)[:NMAX],imstkgr[channel]['DIFF'][:NMAX],dz,outline)
    return result


def roi_to_stkmask(imshape,zgroups,path_circles):
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
    '''
    msk,measure: imagestacks with type bool and float respectively
    dz: relative shift in stack positions at which pixel intensity is measured
    return shape: (#time points, #pixels in msk, # channels)
    '''
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



