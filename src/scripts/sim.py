import sys,os
sys.path.insert(0, os.path.abspath(os.path.join(".")))
import numpy as np

def noise0d(X=128**2,T=240,DT=3,amp=0.1,frac=0.03):#X=128**2,T=240
    '''
    for each x position, choose a fraction of uniformly distributed time points, apply perturbations of duration DT
    '''
    start = np.random.randint(0, T, (X,int(T*frac)))
    duration = DT
    arr = np.zeros((T,X))# shape is (#time points,#spatial points)
    for x in range(X):
        for dt in range(DT):
            arr[np.clip(start[x]+dt,0,T-1),x] = amp
    return arr

def solve_params(a_lst):
    """solve FitzhughNagumo reaction with stochastic perturbation on 1D grid

    run one simulation for each "a" value and save u value at all time points as a tif image with shape ``(T,X^2)``

    Parameters
    ----------
    a_lst : list
        values for parameter "a"
    """

    b_lst=[0.6]
    I_lst=[0.5]
    tau_lst=[10]
    import itertools
    params = list(itertools.product(a_lst, b_lst, I_lst, tau_lst))# list of parameters
    print(params)
    noisearr = noise0d()
    from simrd.fitzhughnagumo import FitzhughNagumo
    from simrd.srd import SRD
    for a, b, I, tau in params:
        ode = FitzhughNagumo(a, b, I, tau)#set parameters
        eq = SRD(noisearr,ode=ode)# set perturbations
        arrtx = eq.solvetx()# solve partial differential equation
        from utils import dir_out,pjoin
        path = pjoin([dir_out,'simrd',str(round(a,3))+'.tif'])
        import tifffile
        tifffile.imsave(path,arrtx)

def freq_wait(a_lst):
    """read u value at all time points, reshape ``(T,X^2)`` to ``(T,X,X)``, calculate frequency and wait time

    Parameters
    ----------
    a_lst : list
        values for parameter "a"

    Returns
    --------
    freq : 1D array
        number of new excitations in every pixel
    wait : 1D array
        number of frames before next new excitation
    """

    from utils import dir_out,pjoin
    from skimage import io
    freq,wait = {},{}
    for a in a_lst:
        path = pjoin([dir_out,'sim',str(round(a,3))+'.tif'])
        im = io.imread(path)
        n2 = int(np.sqrt(im.shape[1]))
        im2 = np.split(im,np.arange(n2,n2**2,n2),axis=1)
        im2 = np.stack(im2,-1)
        EXC = im2>1
        nzzs = np.arange(EXC.shape[0])
        NEWEXC = np.zeros(EXC.shape,bool)
        NEWEXC[nzzs[1:]] = np.diff(EXC[nzzs].astype(int),axis=0)>0

        from measure.recurrence import frequency,waittime
        outline = np.ones(NEWEXC[0].shape,dtype=bool)
        freq[a] = frequency(NEWEXC,outline)
        wait[a] = waittime(NEWEXC,outline,120)
    return freq,wait
    
def axes_sim(fig,freqx,freqy,waitx,waity):
    '''
    Plot histogram of frequency and wait time

    Example::

        figure(pjoin([dir_out,'images']),func=axes_sim,funcdata=[freq_bins/240,freq_hist,wait_bins,wait_hist])
    '''

    W = 2.5
    H = 3.5
    hspace = 0.5
    axes = addax(fig,L=1,W=1.3,T=1,H=1.3)
    axes2 = addax(fig,L=1,W=W,T=5,H=H,ncols=2,nrows=4,wspace=1,hspace=hspace,sharex='col',sharey='col')#,sharey='all'
    axes3 = addax(fig,L=5,W=W,T=5,H=H,ncols=2,nrows=4,wspace=2,hspace=hspace,sharex='col',sharey='col')#,sharey='all'
    axes3tw = np.array([addax(fig,L=6,W=0.2,T=5,H=H,ncols=1,nrows=4,wspace=2,hspace=hspace,sharex='col',sharey='col'),#,sharey='all'
                       addax(fig,L=8,W=0.2,T=5,H=H,ncols=1,nrows=4,wspace=2,hspace=hspace,sharex='col',sharey='col'),]).T

    axes.set(xlim=[-2,2],ylim=[-2,2])
    b=0.6
    I=0.5
    u = np.linspace(-2,2,100)
    ncu = u-(u**3)/3+I
    axes.plot(u,ncu,'k')
    for a in freqy.keys():
        ncv = (u+a)/b
        axes.plot(u,ncv,'--')

    for ax in axes2[1,:]:
        ax.set(ylabel='density')
    for ax in axes2[-1,:]:
        ax.set(ylim=[0,0.8],yticks=[0,0.5],
               xlabel='frequency',xlim=[0,freqx.max()])
    for i,label in enumerate(freqy.keys()):
        xx,yy = step(freqx,freqy[label])
        color = 'darkgray'
        axes2[i,0].fill_between(xx,yy,color=color,lw=0)
        
    for ax in axes3[1,:]:
        ax.set(ylabel='density')
    for ax in axes3[-1,:]:
        ax.set(xlim=[0,120],xlabel='      wait time (s)',xticks=np.arange(0,121,60),ylim=[0,1],yticks=[0,1])
    for i,label in enumerate(waity.keys()):
        x,y = waitx,waity[label]
        xx,yy = step(x[:-1],y[:-1])
        color = 'darkgray'
        axes3[i,0].fill_between(xx,yy,color=color,lw=0)
        axes3tw[i,0].plot(x[-1],y[-1],'x',color=color,lw=10)
    for ax in axes3tw[-1,:]:
        ax.set(xlim=[x[-1]-1,x[-1]+1],xticks=[x[-1]],xticklabels=['>120'],ylim=[0,1],yticks=[0,1])
    

if __name__ == "__main__":
    solve_params(np.arange(0.65,1.1,0.05))

    freq,wait = freq_wait([0.95,0.9,0.85,0.65])

    from utils import dir_out,pjoin
    from visualization.plot import figure,addax,step

    freq_bins = np.arange(12)
    freq_hist = dict(map(lambda kv:(kv[0],np.histogram(kv[1],freq_bins, density=True)[0]), freq.items()))

    dwait = 10
    wait_bins = np.arange(0,121,dwait)
    wait_hist = dict(map(lambda kv:(kv[0],np.histogram(kv[1],wait_bins, density=True)[0]*dwait), wait.items()))

    figure(pjoin([dir_out,'images']),func=axes_sim,funcdata=[freq_bins/240,freq_hist,wait_bins,wait_hist])
    

