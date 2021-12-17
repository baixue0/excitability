'''
plot figures 
'''
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

def figure(savedir,func=None,funcdata=None,figsize=(8.25,11.75),transparent=True,imformat='.svg'):
    #image = figure(pjoin([dir_out,'temp']),func=colorbarfunc,funcdata=[cbar],figsize=(1.4,1.7),imformat='.png')
    #figure(pjoin([dir_out,'temp']),func=colorbarfunc,funcdata=[cbar])
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=figsize,dpi=300)
    path = [savedir,'empty']
    if func is not None and funcdata is not None:
        func(fig,*funcdata)
        path[-1] = func.__name__
    from utils.path_io import pjoin
    path = pjoin(path)+imformat
    if imformat=='.svg':
        fig.savefig(path, transparent=transparent)
        plt.close()
    else:
        fig.savefig(path)
        plt.close()
        from skimage import io
        return io.imread(path)[...,:3].astype(np.uint8)

def addax(fig,L,W,T,H, ncols=1, nrows=1, wspace=0, hspace=0, width_ratios=None, height_ratios=None, sharex='none', sharey='none'):
    FW,FH = fig.get_figwidth(),fig.get_figheight()
    gridspec_kw={'wspace':wspace, 'hspace':hspace, 'width_ratios':width_ratios, 'height_ratios':height_ratios,'left':L/FW, 'right':(L+W)/FW, 'top':1-T/FH,'bottom':1-(T+H)/FH}
    return fig.subplots(ncols=ncols, nrows=nrows, sharex=sharex, sharey=sharey, gridspec_kw=gridspec_kw)

def ax_boxplot(ax,arr,xpositions,widths,colors):
    bp = ax.boxplot(arr, positions=xpositions,widths=widths, vert=True, showfliers=False)#
    for i,color in enumerate(colors):
        for name in ['boxes','medians']:#,'fliers'
            bp[name][i].set_color(color)
        for name in ['whiskers','caps']: 
            bp[name][2*i].set_color(color)
            bp[name][2*i+1].set_color(color)

def step(xedges,y):#xedges.shape is (N+1,); y.shape is (N,)
    N = len(xedges)-1
    result = []
    for i in range(N-1):
        result += [(xedges[i],y[i]),(xedges[i+1],y[i])]
    result += [(xedges[N-1],y[N-1]),(xedges[N],y[N-1])]
    return np.array(result).T

def setlogy(ax,ylim):
    ax.set(yscale="log",ylabel='Fraction')
    locmin = matplotlib.ticker.LogLocator(base=10.0,subs=(0.2,0.4,0.6,0.8),numticks=5)
    ax.yaxis.set(minor_locator=locmin, minor_formatter=matplotlib.ticker.NullFormatter())
    ax.set(yticks=[10.0**v for v in np.arange(-6,5)],ylim=ylim)


legends = {
'spd':('   control','dimgray'),
'cyk':('CYK-1 (RNAi)','mediumturquoise'),
'ani':('ANI-1 (RNAi)','hotpink'),
'pfn':('PFN (RNAi)',''),
'nmy':('NMY-2 (ts)',''),
'mel11':('MEL-11 (RNAi)',''),
'plst':('PLST-1 (TM2455)',''),
'unc60':('UNC-60 (RNAi)',''),
}

