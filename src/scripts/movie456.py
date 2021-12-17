import sys
sys.path.insert(0, "..")# Adds higher directory to python modules path.

from utils.path_io import *
from utils.decorators import repeat
global result

def colorbar5(fig,cbar):
    from plot import addax
    ax = addax(fig,L=0.8,W=0.3,T=0.2,H=1)
    N = cbar.shape[0]
    ax.imshow(cbar,extent=(-6,0,N,0),aspect='auto')
    ax.set(xticks=[-6,0],yticks=[0,N],
           yticklabels=['large','small'],
           xlabel='time (s)',ylabel='linked groups')
def colorbar4(fig,cbar):
    from plot import addax
    ax = addax(fig,L=0.8,W=0.3,T=0.2,H=1)
    N = cbar.shape[0]
    ax.imshow(cbar,extent=(-6,0,N,0),aspect='auto')
    ax.set(xticks=[-6,0],yticks=[],xlabel='time (s)')
    ax.set_ylabel(ylabel='excitation\nregions', labelpad=20)

def colorbar6(fig,cbar):
    from plot import addax
    ax = addax(fig,L=0.8,W=0.3,T=0.2,H=1)
    ax.imshow(cbar,extent=(0,1,-4,4),aspect='auto')
    ax.set(xticks=[],yticks=[-4,-2,0,2,4],ylabel='F-actin normalized\ntemporal derivative')

def drawstk4(blobs,imshape): 
    from fadingexc import fade
    fade(np.array([[0.3]*3]),blobs,imshape)

def drawstk5(blobs,imshape):
    from fadingexc import dark_unique_colors,fade
    fade(dark_unique_colors(),blobs,imshape)

def drawstk6(DIFF,blobs,imshape):
    from matplotlib.colors import LinearSegmentedColormap
    cmap_diff = LinearSegmentedColormap.from_list('diff', [[i/2,c] for i,c in enumerate(['#85cc90','#f2f2f2','#cc85c0'])])
    from image import interpcolor,sqrt_across_zero
    stk = interpcolor(sqrt_across_zero(DIFF),(-np.sqrt(4),np.sqrt(4)),cmap_diff)
    cbar = np.expand_dims(np.linspace(-4,4,100),-1)
    cbar = interpcolor(sqrt_across_zero(cbar),(-np.sqrt(4),np.sqrt(4)),cmap_diff)
    return stk,cbar

def fademask(stk,msk,N=5):
    from fadingexc import linearinterpcolor
    for z in range(N,stk.shape[0]):
        zs = np.arange(z-N,z+1)
        for zz in zs:
            stk[z,msk[zz]] = linearinterpcolor(zz-zs[0],0,zs[-1]-zs[0],tuple([200/255]*3),tuple([0.3]*3))

if __name__ == "__main__":
    embryos_example = embryos.loc[['20190524_7','20190803_19','20190729_12']]
    result = {}
    @repeat(embryos_example,result,shuffle=False)
    def movie456(phenotype,ID):
        dir_thresh = str(0.4)
        result_excitation = load_dict(pjoin([dir_out,dir_thresh,'excitation',ID]))
        NMAX = 100
        EXC,NEWEXC = result_excitation['EXC'][:NMAX],result_excitation['NEWEXC'][:NMAX]
        from measure.contour import findContours
        blobs = findContours(EXC,minarea=2**2)
        from measure.link import connected_components
        blobs, graph, cc, area = connected_components(blobs,example=True)
        
        stk456,title456,cbar456 = {},{},{}
        for i,(drawstkfunc,colorbarfunc) in enumerate([(drawstk4,colorbar4),(drawstk5,colorbar5),(drawstk6,colorbar6)]):#
            if i==2:
                input = load_dict(pjoin([dir_out,'stepGroupDiff',ID]))
                DIFF = input['imr']['DIFF'][:100]
                stk,cbar = drawstkfunc(DIFF,blobs,EXC.shape)
                fademask(stk,NEWEXC,N=3)
                stk = stk[4:]
            else:
                stk,cbar = drawstkfunc(blobs,EXC.shape)
                stk = stk[:-5]
            from movie import rotate
            stk = rotate(pjoin([dir_data,directories['outline'],'poly-'+ID+'.tif']),stk)
            from movie import create_title
            from plot import legends
            title = create_title(stk.shape,legends[phenotype][0])
            stk456[i+4],title456[i+4] = stk,title
            if ID=='20190524_7':
                from plot import figure
                cbar456[i+4] = figure(pjoin([dir_out,'temp']),func=colorbarfunc,funcdata=[cbar],figsize=(1.4,1.7),imformat='.png')
        return stk456,title456,cbar456
    movie456()
    from movie import boarder
    for movieid in [4,5,6]:
        bottom = np.dstack([boarder(result[ID][0][movieid],(0,0,2,2),padcolor=(255,255,255)) for ID in embryos_example.index])
        from movie import time_scalebar
        bottom = time_scalebar(bottom,dt=1.2,textcolor=(0,0,0))
        top = np.dstack([boarder(result[ID][1][movieid],(0,0,2,2),padcolor=(255,255,255)) for ID in embryos_example.index])
        N = bottom.shape[0]
        ID = list(embryos_example.index)[0]
        cbarim = result[ID][2][movieid].copy()
        targetshape0 = bottom.shape[1]
        scale = targetshape0/cbarim.shape[0]
        targetshape1 = int(scale*cbarim.shape[1])
        import cv2
        cbarim2 = cv2.resize(cbarim, dsize=(targetshape1,targetshape0))
        cbarstk = np.stack([cbarim2]*N,0)
        print(top.shape,bottom.shape,cbarstk.shape)
        from movie import saveMP4,stk_upsizexy
        right = np.hstack([top,bottom])
        left = np.full((right.shape[0],right.shape[1],cbarstk.shape[2],right.shape[3]),255,dtype=np.uint8)
        left[:,-cbarstk.shape[1]:,:,:]=cbarstk
        tosave = np.dstack([left,right])
        tosave = stk_upsizexy(tosave,2)
        saveMP4(pjoin([dir_out,'images',['movie',str(movieid)]]), tosave, 20)
