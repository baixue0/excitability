import sys,os
sys.path.insert(0, os.path.abspath(os.path.join(".")))
import numpy as np
from visualization.plot import figure, addax, legends
from utils import pjoin, dir_out, embryos, load_dict

def axes_freq(fig,x,y):
    '''
    Plot histogram of frequency

    This function is passed to ``visualization.plot.figure``

    :param fig: the figure to plot on
    :type fig: matplotlib.pyplot.figure
    :param x: a dictionary of x coordinates ``str:np.array((n,))``
    :type x: dict
    :param y: a dictionary of y coordinates ``str:np.array((n,))``
    :type y: dict
    :rtype: None

    Example::

        figure(pjoin([dir_out,'images']),func=axes_freq,funcdata=[freq_bins/120,freq_hist])
    '''
    axes_speed = addax(fig,L=1,W=2,T=0.5,H=2,ncols=2,nrows=3,wspace=1,hspace=0.5,sharex='all',sharey='col')
    for ax in axes_speed[1,:]:
        ax.set(ylabel='density')
    for ax in axes_speed[-1,:]:
        ax.set(ylim=[0,0.4],yticks=[0,0.3],
               xlabel='frequency',xlim=[0,x.max()])
    for i,phenotype in enumerate(['spd','cyk','ani']):
        xx,yy = step(x,y[phenotype])
        color = legends[phenotype][1]
        axes_speed[i,0].fill_between(xx,yy,color=color,alpha=0.5,lw=0)
        axes_speed[i,1].fill_between(xx,yy,color=color,alpha=0.5,lw=0)
    for i,phenotype in enumerate(['nmy','cyk+nmy','ani+nmy']):
        xx,yy = step(x,y[phenotype])
        color = 'slateblue'
        axes_speed[i,1].plot(xx,yy,color=color)

def axes_wait(fig,x,y):
    '''    
    Plot histogram of wait time

    Example::

        figure(pjoin([dir_out,'images']),func=axes_wait,funcdata=[wait_bins*1.2,wait_hist])
    '''
    W = 3
    H = 2
    hspace = 0.5
    axes = addax(fig,L=1,W=W,T=1,H=H,ncols=2,nrows=3,wspace=2,hspace=hspace,sharex='col',sharey='col')
    #axestw has the same shape as axes
    axestw = np.array([addax(fig,L=2.2,W=0.2,T=1,H=H,ncols=1,nrows=3,wspace=2,hspace=hspace,sharex='col',sharey='col'),
                       addax(fig,L=4.45,W=0.2,T=1,H=H,ncols=1,nrows=3,wspace=2,hspace=hspace,sharex='col',sharey='col'),]).T
    for ax in axes[1,:]:
        ax.set(ylabel='density')
    for ax in axes[-1,:]:
        ax.set(xlim=[0,60],xlabel='      Wait time (s)',xticks=[0,20,40,60],ylim=[0,0.06])
    for ax in axestw[-1,:]:
        ax.set(xlim=[59,61],xticks=[60],xticklabels=['>60'],ylim=[0,0.5],yticks=[0,0.5])
    for i,phenotype in enumerate(['spd','cyk','ani']):
        print(x[:-1],y[phenotype][:-1])
        xx,yy = step(x[:-1],y[phenotype][:-1])
        color = legends[phenotype][1]
        axes[i,0].fill_between(xx,yy,color=color,alpha=0.5,lw=0)
        axes[i,1].fill_between(xx,yy,color=color,alpha=0.5,lw=0)
        axestw[i,0].plot(x[-1],y[phenotype][-1],'+',color=color)
        axestw[i,1].plot(x[-1],y[phenotype][-1],'+',color=color)
    for i,phenotype in enumerate(['nmy','cyk+nmy','ani+nmy']):
        xx,yy = step(x[:-1],y[phenotype][:-1])
        color = 'slateblue'
        axes[i,1].plot(xx,yy,color=color)
        axestw[i,1].plot(x[-1],y[phenotype][-1],'+',color=color)

def axes_speed(fig,x,y):
    '''
    Plot histogram of speed of excitation fronts

    Example::

        figure(pjoin([dir_out,'images']),func=axes_speed,funcdata=[speed_bins*0.1/1.2,speed_hist])
    '''
    
    axes_speed = addax(fig,L=1,W=1.75,T=0.5,H=1.2,ncols=2,nrows=3,wspace=1,hspace=0.5,sharex='col',sharey='none',width_ratios=(2,1))
    axes_speed[1,0].set(ylabel='density')
    axes_speed[-1,1].set(xlabel='speed (${\mu}m/s$)')
    threshold = 2
    for i,phenotype in enumerate(['spd','cyk','ani']):
        xx,yy = step(x,y[phenotype])
        
        axes_speed[i,0].fill_between(xx,yy,color=legends[phenotype][1],alpha=0.5,lw=0)
        axes_speed[i,0].set(xlim=[xx[0],xx[-1]],xticks=[xx[0],xx[-1]],xticklabels=[np.round(xx[0],2),np.round(xx[-1],2)],
                          ylim=[0,0.6],yticks=[0,0.6])
        axes_speed[i,0].axvline(x[3],color='k',ls=':')
        
        xx,yy = step(x[threshold+1:],y[phenotype][threshold+1:])
        axes_speed[i,1].fill_between(xx,yy,color=legends[phenotype][1],alpha=0.5,lw=0)
        axes_speed[i,1].set(xlim=[xx[0],xx[-1]],xticks=[xx[0],xx[-1]],xticklabels=[np.round(xx[0],2),np.round(xx[-1],2)],
                            ylim=[0,0.1],yticks=[0,0.1])

def axes_area(fig,x):
    '''
    Plot histogram of largest cumulative are of linked groups

    Example::

        figure(pjoin([dir_out,'images']),func=axes_area,funcdata=[area])
    '''
    axes = addax(fig,L=1,W=3,T=0.5,H=1,ncols=2,nrows=1,wspace=1,hspace=0.5)
    for ax in axes:
        ax.set(ylim=[0,100],yticks=np.arange(0,101,50),ylabel='cumulative area\n(% embryo)')
    phenotypelst = ['spd','cyk','ani']
    xx = x.loc[phenotypelst]
    colors = [legends[phenotype][1] for phenotype in phenotypelst]
    ax_boxplot(axes[0],x,np.arange(3),0.5,colors)
    ax_boxplot(axes[1],x,np.arange(3)-0.15,0.3,colors=colors)
    phenotypelst = ['nmy','cyk+nmy','ani+nmy']
    xx = x.loc[phenotypelst]
    ax_boxplot(axes[1],x,np.arange(3)-0.15,0.3,colors=['slateblue']*3)
    for ax in axes:
        ax.set(xticks=[])

def axes_actin(fig,x):
    '''
    Plot average F-actin level in new excitation pixels

    Example::

        figure(pjoin([dir_out,'images']),func=axes_actin,funcdata=[meandict])
    '''
    dz=np.arange(-15,6)
    m = np.logical_and(dz>=-5,dz<=5)
    t = dz[m]*1.2
    axes = addax(fig,L=1,W=5.5,T=1,H=4,ncols=4,nrows=3,wspace=0.5,hspace=1,sharey='row')
    for ax in [*axes[1],*axes[2]]:
        ax.set(xlabel='time offset (s)',ylim=[-1.5,1.5])
    for ax in axes[:,0]:
        ax.set(ylabel='F-actin\ntemporal derivative')
    for i,phenotype in enumerate(['spd','cyk','ani']):
        color = legends[phenotype][1]
        axes[0,i].plot(t,x['newexc_imr_raw'][phenotype][m],color=color)
        axes[0,-1].plot(t,x['newexc_imr_raw'][phenotype][m],color=color)
        axes[1,i].plot(t,x['newexc_imr_diff'][phenotype][m],color=color)
        axes[2,i].plot(t,x['fast_imr_diff'][phenotype][m],color='darkorange')
        axes[2,i].plot(t,x['slow_imr_diff'][phenotype][m],color='dodgerblue')

def axes_acf(fig,x):
    '''
    Plot average autocorrelation function of pixels in embryos

    Example::

        figure(pjoin([dir_out,'images']),func=axes_acf,funcdata=[meandict])

    '''
    dz = np.arange(-97,98)
    m = np.abs(dz)<40
    mhalf = np.logical_and(dz>=0,dz<40)
    axes = addax(fig,L=1,W=4,T=1,H=1.2,ncols=2,nrows=1,wspace=1,hspace=1)
    ax2 = addax(fig,L=1,W=3,T=3,H=1.2)

    for i,phenotype in enumerate(['spd','cyk','ani']):
        color = legends[phenotype][1]
        axes[0].plot(dz[mhalf]*1.2,x['acfrect_smooth'][phenotype][mhalf],color=color)
        axes[1].plot(dz[mhalf]*1.2,x['acf_smooth'][phenotype][mhalf],color=color)
        ax2.plot(dz[m]*1.2,x['ccf_smooth'][phenotype][m],color=color)
    for ax in axes:
        ax.set(xlabel='timelag (s)',xticks=np.arange(0,41,20),xlim=[dz[mhalf][0]*1.2,dz[mhalf][-1]*1.2],
        ylim=[-0.5,1])#ylabel='correlation',

    ax2.set(xlabel='timelag (s)',xticks=np.arange(-40,41,20),xlim=[dz[m][0]*1.2,dz[m][-1]*1.2],
    ylim=[-0.5,1])#ylabel='correlation',


if __name__ == "__main__":
    direxc = '0.4'
    
    from scripts.quant import selectEmbryo
    embryosquant = selectEmbryo(embryos)

    groups = embryosquant.groupby('phenotype')
    groupsR = embryosquant.loc[embryosquant['LabelR']=='LA'].groupby('phenotype')

    '''
    hstack_hist = lambda datadict,IDs,bins: np.histogram(np.hstack([datadict[ID] for ID in IDs]),bins)[0]

    datadict = load_dict(pjoin([dir_out,direxc,'summary','freq']))
    freq_bins = np.arange(12)
    freq_hist = groups.apply(lambda groupdf: hstack_hist(datadict,groupdf.index,freq_bins))
    figure(pjoin([dir_out,'images']),func=axes_freq,funcdata=[freq_bins/120,freq_hist])

    datadict = load_dict(pjoin([dir_out,direxc,'summary','wait']))
    wait_bins = np.arange(51)
    wait_hist = groups.apply(lambda groupdf: hstack_hist(datadict,groupdf.index,wait_bins))
    figure(pjoin([dir_out,'images']),func=axes_wait,funcdata=[wait_bins*1.2,wait_hist])

    datadict = load_dict(pjoin([dir_out,direxc,'summary','speed']))
    speed_bins = np.arange(12)
    speed_hist = groups.apply(lambda groupdf: hstack_hist(datadict,groupdf.index,speed_bins))
    figure(pjoin([dir_out,'images']),func=axes_speed,funcdata=[speed_bins*0.1/1.2,speed_hist])

    datadict = load_dict(pjoin([dir_out,direxc,'summary','area']))
    area = groups.apply(lambda groupdf: [datadict[ID]*100 for ID in groupdf.index])
    figure(pjoin([dir_out,'images']),func=axes_area,funcdata=[area])
    '''

    vstack_mean = lambda datadict,IDs: np.vstack([datadict[ID] for ID in IDs]).mean(0)
    meandict = {}
    for name in [
    #'newexc_imr_raw','newexc_imr_diff','fast_imr_diff','slow_imr_diff',
    'acfrect_smooth','ccf_smooth','acf_smooth',
    ]:
        datadict = load_dict(pjoin([dir_out,direxc,'summary',name]))
        print(name,next(iter(datadict.values())).shape)
        meandict[name] = groups.apply(lambda groupdf: vstack_mean(datadict,groupdf.index))
    #figure(pjoin([dir_out,'images']),func=axes_actin,funcdata=[meandict])
    figure(pjoin([dir_out,'images']),func=axes_acf,funcdata=[meandict])

