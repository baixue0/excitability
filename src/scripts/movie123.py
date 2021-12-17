import sys,os
sys.path.insert(0, os.path.abspath(os.path.join(".")))

from utils.path_io import *
from utils.decorators import iterate

def read(phenotype,ID):
    from measure.preprocess import read_raw
    dir_raw = pjoin([dir_data,directories['rawtif'],phenotype,ID])
    result_read_raw = read_raw([dir_out,'',ID],dir_raw,ID,embryos.loc[ID]['LabelR'],embryos.loc[ID]['tRes'],embryos.loc[ID]['nEnd'])
    #write_proj(pjoin([dir_data,directories['outline'],ID+'.tif']),result[ID]['img'])
    return result_read_raw

def movie123(phenotype,ID):
    from measure.preprocess import read_outline
    outline = read_outline(pjoin([dir_data,directories['outline'],'poly-'+ID+'.tif']))
    from visualization.rotate_crop import Rotate_Crop
    RC = Rotate_Crop(outline)

    result_read_raw = load_dict(pjoin([dir_out,'read_raw',ID]))
    from visualization.image import vminmax_raw,interpcolor
    stk = result_read_raw['img'][:200].copy()
    from measure.segmentation import moving_avg
    groupsize = 2
    stk = moving_avg(stk,groupsize)
    import cv2
    for i in range(groupsize,stk.shape[0]-groupsize):
        stk[i] = cv2.medianBlur(stk[i],5)
    #import tifffile
    #tifffile.imsave(pjoin([dir_out,'images','movie1',phenotype])+'.tif', stk.astype(np.uint16))
    #'''
    stk = interpcolor(stk,minmax_g_dict[phenotype],'gray')
    stk = RC.rotate_stk(stk,0)
    stk = stk[groupsize:-groupsize]
    from visualization.movie import create_title
    from visualization.plot import legends
    title = create_title(stk.shape,legends[phenotype][0])
    #'''
    return stk,title

if __name__ == "__main__":
    examples = {
        'mel11':'20210420_23',
        'unc60':'20210410_11',
        'ani':'20190729_10',
        'nmy':'20191108_15',
        'spd':'20210420_29',
        'cyk':'20190803_19',
        'plst':'20210409_7',
        'pfn':'20191026_8'}
    
    embryos_example = embryos.loc[examples.values()]
    result = iterate(read,embryos_example,shuffle=False)
    iterate(movie123,embryos_example,result=result,shuffle=False)
        
    minmax_g_dict = {'spd':(0,1300),'cyk':(150,800),'ani':(100,1100),
                     'nmy':(200,1300),'mel11':(0,1200),'plst':(0,1200),
                     'unc60':(0,1300),'pfn':(0,1200)}

    for i,phenotypes in enumerate([['spd','cyk','ani'],['spd','nmy','mel11','plst'],['spd','unc60']]):
        IDs = [examples[phenotype] for phenotype in phenotypes]
        from visualization.movie import boarder,time_scalebar
        bottom = np.dstack([boarder(result[ID][0],(0,0,2,2),padcolor=(255,255,255)) for ID in IDs])
        bottom = time_scalebar(bottom,dt=0.6,textcolor=(255,255,255))

        top = np.dstack([boarder(result[ID][1],(0,0,2,2),padcolor=(255,255,255)) for ID in IDs])
        from visualization.movie import saveMP4,stk_upsizexy
        tosave = stk_upsizexy(np.hstack([top,bottom]),2)
        saveMP4(pjoin([dir_out,'images',['movie',str(i+1),''.join(phenotypes)]]), tosave, 20)#stack top bottom


