import numpy as np

def fade(colors,blobs,imshape,N=5):
    gray = tuple([235/255]*3)
    indexcolor = lambda label:colors[label%len(colors)]
    stk = np.full([*imshape,3],235,dtype=np.uint8)
    for z in blobs.keys():
        for b in blobs[z]:
            if not hasattr(b,'label'):
                continue
            x,y = b.pixels.T
            saturated = indexcolor(b.label)
            for dz in np.arange(-N,1):
                znew = z+dz
                if znew<0:
                    continue
                stk[znew,x,y] = linearinterpcolor(dz,(-N,1),(saturated,gray))
    cbar = np.array([[linearinterpcolor(dz,(-N,1),(indexcolor(label),gray)) for dz in np.flip(np.arange(-N,1))] for label in range(10)])
    return stk,cbar

def linearinterpcolor(v,vminmax,colorminmax):
    """convert number or array to RGB color given the colors at extremes of LinearSegmentedColormap

    Parameters
    ----------
    v : number or ndarray with dimention 1, 2 or 3
        value to be converted to RGB color
    vminmax : tuple
        (vmin,vmax) to normalize v
    colorminmax : tuple
        (colormin,colormax) at extremes of LinearSegmentedColormap

    Returns
    --------
    rgb255 : same shape as v, dtype=np.uint8
        converted value
        
     """

    from matplotlib.colors import LinearSegmentedColormap
    cmap = LinearSegmentedColormap.from_list('', [(i,c) for i,c in enumerate(colorminmax)])
    from visualization.image import interpcolor
    return interpcolor(v,vminmax,cmap)

def dark_unique_colors():
    import colorcet as cc#https://colorcet.holoviz.org/
    cmap = cc.cm.glasbey_category10
    arr = cmap(np.arange(256))[:,:3]
    #ix1,ix2 = 1,-1
    #arr[ix1], arr[ix2] = arr[ix2], arr[ix1]
    return arr
