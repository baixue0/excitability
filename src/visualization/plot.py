'''
plot figures 
'''
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

def figure(savedir,func,funcdata,figsize=(8.25,11.75),imformat='.svg'):
    """create and plot on a figure using func and funcdata

    Parameters
    ----------
    savedir : str
        directory to save figure
    func : function
        a function that takes ``phenotype`` and ``ID`` as the first two arguments with additional positional and/or keyword arguments
    funcdata : iterable
        data to unpack and pass to func

    Examples
    --------
    .. code-block:: python

        def axes_a(fig,x,y):
            ax = addax(fig,L=1,W=2,T=0.5,H=2)
            ...

        figure(directory, axes_a, (x,y))
        # figure is saved as 'directory/axes_a.svg'

    """

    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=figsize,dpi=300)
    func(fig,*funcdata)
    from utils import pjoin
    path = pjoin([savedir,func.__name__+imformat])
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
    gridspec_kw={'wspace':wspace, 'hspace':hspace, 
    'width_ratios':width_ratios, 'height_ratios':height_ratios,
    'left':L/FW, 'right':(L+W)/FW, 
    'top':1-T/FH,'bottom':1-(T+H)/FH}
    return fig.subplots(ncols=ncols, nrows=nrows, sharex=sharex, sharey=sharey, gridspec_kw=gridspec_kw)

def ax_boxplot(ax,arr,xpositions,widths,colors):
    bp = ax.boxplot(arr, positions=xpositions,widths=widths, vert=True, showfliers=False)#
    for i,color in enumerate(colors):
        for name in ['boxes','medians']:#,'fliers'
            bp[name][i].set_color(color)
        for name in ['whiskers','caps']: 
            bp[name][2*i].set_color(color)
            bp[name][2*i+1].set_color(color)

def step(x,y):#xedges.shape is (N+1,); y.shape is (N,)
    """helper function for plotting histograms

    Parameters
    ----------
    x : np.array((N+1,),dtype=float)
        x value of histogram
    y : np.array((N,),dtype=float)
        y value of histogram

    Examples
    --------
    .. code-block:: python

        ax.fill_between(*step(x,y))
    """

    N = len(x)-1
    result = []
    for i in range(N-1):
        result += [(x[i],y[i]),(x[i+1],y[i])]
    result += [(x[N-1],y[N-1]),(x[N],y[N-1])]
    return np.array(result).T

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

