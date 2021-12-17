import numpy as np

def interpcolor(v,norm,cmap,rgb_only=True):
    from matplotlib.colors import Normalize
    norm = Normalize(vmin=norm[0],vmax=norm[1])
    import matplotlib
    m = matplotlib.cm.ScalarMappable(norm=norm, cmap=cmap)
    if hasattr(v,'ndim'):
        ndim = v.ndim
        if ndim<3:
            result = np.array(m.to_rgba(v))*255
        else:
            result = np.stack([np.array(m.to_rgba(v[z]))*255 for z in range(v.shape[0])],0)
    else:
        result = np.array(m.to_rgba(v))*255
    result = result.astype(np.uint8)
    if rgb_only:
        result = result[...,:3]
    return result

def namedcolor_to_rgb(namedcolor):
    import matplotlib
    return np.array(matplotlib.colors.to_rgba(namedcolor)[:-1])*255

def standarize(arr,vmin,vmax):
    if vmin is None or vmax is None:
        return arr
    arr2 = np.clip(arr,vmin,vmax)
    return (arr2-vmin)/(vmax-vmin)

def merge_magenta_green(magenta,green):
    rgb = np.stack([magenta,green,magenta],-1)
    return (rgb*255).astype(np.uint8)
    
def vminmax_raw(imstk,outline,percentile=[0.005,99.9]):
    nzzs = np.where(imstk.max(1).max(1))[0]
    arr = imstk[nzzs]
    if outline is not None:
        arr = arr[:,outline]
    return np.percentile(arr.ravel(),percentile)

def sqrt_across_zero(arr):
    return np.sqrt(np.abs(arr))*np.sign(arr)
