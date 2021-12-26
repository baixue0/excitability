import sys,os
sys.path.insert(0, os.path.abspath(os.path.join(".")))
from utils.path_io import *
from utils.decorators import iterate,return_dict

"""pipeline to batch measure embryo"""

def selectEmbryo(embryos):
    """Select embryos to quantify

    embryos to quantify should satisfy the following conditions

    - green channel label is ROK
    - phenotype is not pfn
    - duration of image stack is longer than 130 seconds

    Parameters
    ----------
    embryos : `pandas.DataFrame`
        all embryos

    Returns
    --------
    embryosquant : `pandas.DataFrame`
        selected embryos
    """

    df = pd.concat([embryos['LabelG']=='ROK', # green channel label is ROK
               embryos['phenotype']!='pfn', # phenotype is not pfn
               embryos['note'].str.startswith('SD'),# image is acquired with spinning disk microscopy
               pd.Series(embryos['nEnd']*embryos['tRes']>130,name='long'),# duration of image stack is longer than 130 seconds
               pd.Series(np.logical_not(embryos.index.str.startswith('2021')),index=embryos.index,name='before2021'),# excludes embryos imaged in 2021
              ], axis=1)# stack colums left to right
    embryosquant = embryos.loc[df.all(1)]# select rows that satisfy all conditions above
    return embryosquant

def stepRaw(phenotype,ID):
    '''
    read raw 16-bit tif files

    save as python dictionary for each embryo

    export mean projection of green channel as tiff files

    label outline of embryo in ImageJ manually and save as binary masks
    '''
    from measure.preprocess import read_raw
    dir_raw = pjoin([dir_data,directories['rawtif'],phenotype,ID])
    result_read_raw = read_raw([dir_out,'',ID],dir_raw,ID,embryos.loc[ID]['LabelR'],embryos.loc[ID]['tRes'],embryos.loc[ID]['nEnd'])#read raw 16-bit tif files
    import tifffile
    tifffile.imsave(pjoin([dir_data,directories['outline'],ID+'.tif']),result_read_raw['img'][:100].mean(0).astype(np.uint16))#save as python dictionary for each embryo
    return result_read_raw

def stepGroupDiff(phenotype,ID,run=True):
    '''
    read binary mask of the outline of the embryo

    read raw 16-bit tif files

    subtract photobleach trend in time for all pixels in each frame

    calculate grouped average and derivative in time
    '''
    path = pjoin([dir_out,'stepGroupDiff',ID])
    if not run:
        print('load',end=' ')
        return load_dict(path)
    result = {}
    tRes = embryos.loc[ID]['tRes']
    from measure.preprocess import read_outline
    result['outline'] = read_outline(pjoin([dir_data,directories['outline'],'poly-'+ID+'.tif']))#read binary mask of the outline of the embryo

    from measure.segmentation import bleach_correction,group_diff
    result_read_raw = load_dict(pjoin([dir_out,'read_raw',ID]))#read raw 16-bit tif files
    from measure.preprocess import divide
    window_length, videozmin = divide(40,tRes)*2+1, divide(100,tRes)
    from measure.preprocess import channel_list
    for channel in channel_list(ID,embryos):
        result[channel] = {}
        _,_,result[channel]['bc'] = bleach_correction(result_read_raw[channel], result['outline'], window_length, videozmin)#subtract photobleach trend in time for all pixels in each frame
        result[channel].update(group_diff(result[channel]['bc'],result['outline'],tRes))#calculate grouped average and derivative in time
    np.save(path,result)
    return result

def writeThreshold(path,embryosquant,result_grouped):
    '''
    calculate and write intensity of maunally labeled pulsing pixels
    '''
    dz=np.arange(-15,6)
    from measure.pixel_intensity import roi_to_stkmask,intensity_ts
    diffts = {}
    for ID in embryosquant.index:
        path_circles = pjoin([dir_data,directories['circles'], [embryosquant.loc[ID]['phenotype'],ID]])+'.zip'#path of manually labeled excitation circles
        if not pexists(path_circles):
            diffts[ID] = None
            continue
        resultgroupedID = result_grouped[ID]
        DIFF,zgroups,outline = resultgroupedID['img']['DIFF'],resultgroupedID['img']['zgroups'],resultgroupedID['outline']
        circles_mask = roi_to_stkmask(DIFF.shape,zgroups,path_circles)#read manually labeled excitation circles
        diffts[ID] = intensity_ts(circles_mask,DIFF,dz,outline)
    diffts_group_vstack = embryosquant.groupby('phenotype').apply(lambda group: np.vstack([diffts[ID] for ID in group.index if diffts[ID] is not None]))#measure intensity of temporal derivative in excitation circles
    np.save(path,diffts_group_vstack.to_dict())

def readThreshold(path,embryosquant,THRESHOLD):
    '''
    read intensity of maunally labeled pulsing pixels

    calculate threshold value for each phenotype

    assign threshold value to each embryo based on its phenotype
    '''
    diffts = load_dict(path)
    df_threshold = pd.DataFrame({i:[phenotype,arr.mean(0).max()*THRESHOLD] for i,(phenotype, arr) in enumerate(diffts.items())}).T
    df_threshold.columns=['phenotype','threshold']
    return embryosquant.reset_index().merge(df_threshold, how="left").set_index('ID')

def stepExcitation(phenotype,ID,THRESHOLD):
    '''
    read binary mask of the outline of the embryo

    use temporal derivative and threshold value to calculate binary mask of excitation and new excitation
    '''
    data_GroupDiff = load_dict(pjoin([dir_out,'stepGroupDiff',ID]))
    from measure.segmentation import excitation
    result_excitation = excitation([dir_out,str(THRESHOLD),'',ID], data_GroupDiff['img']['DIFF'],data_GroupDiff['outline'],embryosquant.loc[ID]['threshold'])#calculate binary mask of excitation and new excitation
    
    return result_excitation

def stepSummary(phenotype,ID,THRESHOLD):
    '''
    calculate summary statistics from binary masks of excitations and newexcitations

    calculate average F-actin level in newexcitation pixels

    calculate average autocorrelation of ROK level in all pixels in the embryo
    '''
    result = {}
    result_excitation = load_dict(pjoin([dir_out,str(THRESHOLD),'excitation',ID]))
    EXC,NEWEXC,outline = result_excitation['EXC'],result_excitation['NEWEXC'],result_excitation['outline']
    result.update(summary_exc(EXC,NEWEXC,outline))

    data_GroupDiff = load_dict(pjoin([dir_out,'stepGroupDiff',ID]))
    from measure.pixel_intensity import ts_embryo
    result.update(ts_embryo(data_GroupDiff,NEWEXC,result['speedmsk'],NMAX=100))

    result.pop('speedmsk', None)
    return result

@return_dict
def summary_exc(EXC,NEWEXC,outline,NMAX=100):
    """calculate summary statistics from binary masks of excitations and newexcitations

    Parameters
    ----------
    EXC : np.array((T,X,Y),dtype=bool)
        excitation mask
    NEWEXC : np.array((T,X,Y),dtype=bool)
        new excitation mask
    outline : np.array((X,Y),dtype=bool)
        mask of pixels in embryo

    Returns
    --------
    freq : 1D array
        number of new excitations in every pixel
    wait : 1D array
        number of frames before next new excitation
    speed : 1D array
        distance from point to edge of new excitation regions
    speedmsk : np.array((T,X,Y),dtype=np.float32)
        pixel value represents amplitude of edge propagation. pixels outside of embryo are labeled -1.
    area : 1D array
        largest cumulative are of linked excitation regions
    """

    from measure.recurrence import frequency,waittime
    freq = frequency(NEWEXC[:NMAX],outline)#frequency of new excitations
    wait = waittime(NEWEXC[:NMAX],outline,50)#wait time of new excitations

    from measure.contour import findContours
    blobs = findContours(EXC[:NMAX],minarea=2**2)# dictionary of Blob instances that defines one excitation region

    from measure.edgespeed import point_velocity
    speed, speedmsk = point_velocity(blobs,NEWEXC[:NMAX+1],outline)#edge propagation speed of excitation regions

    from measure.link import connected_components
    area = connected_components(blobs)#cumulative area of linked excitation regions
    area = area/outline.sum()
    
    return freq,wait,speed,area,speedmsk

def reorder(nesteddict):
    '''
    Flip the order of a nested dictionary

    :param nesteddict: ``{ID0:{'x':x,'y':y}, ID1:{'x':x,'y':y}, ...}``
    :type nesteddict: dict
    :return: ``{'x':{ID0:x,'ID1':x}, 'y':{ID0:y,'ID1':y}, ...}``
    :rtype: dict
    '''
    return pd.DataFrame(nesteddict).transpose().to_dict()

if __name__ == "__main__":
    embryosquant = selectEmbryo(embryos)
    #iterate(stepRaw,embryosquant)
    #result_grouped = iterate(stepGroupDiff,embryosquant)
    #result_grouped = iterate(stepGroupDiff,embryosquant,run=False)
    path_threshold_diffts = pjoin([dir_out,'threshold_diffts'])
    #writeThreshold(path_threshold_diffts,embryosquant,result_grouped)
    for THRESHOLD in [0.4,]:#0.4,0.36,0.44
        embryosquant = readThreshold(path_threshold_diffts,embryosquant,THRESHOLD)
        #result_excitation = iterate(stepExcitation,embryosquant,THRESHOLD)
        result_summary = iterate(stepSummary,embryosquant,THRESHOLD, shuffle=False)
        for name,value in reorder(result_summary).items():
            np.save(pjoin([dir_out,str(THRESHOLD),'summary',name]),value)




