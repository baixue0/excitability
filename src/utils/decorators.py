import numpy as np
from utils.path_io import pjoin

def iterate(func,embryos,*args,result={},shuffle=True,**kwargs):
    """apply func to each embryo

    Parameters
    ----------
    func : function
        a function that takes ``phenotype`` and ``ID`` as the first two arguments with additional positional and/or keyword arguments
    embryos : pandas.DataFrame
        each line specifies the ``phenotype`` , ``ID`` and other information about an embryo

    Returns
    -------
    dict
        ``{ID:func(phenotype,ID,*args,**kwargs)}``

    """

    IDs = list(embryos.index.copy())
    if shuffle:
        import random
        random.shuffle(IDs)
    from datetime import datetime
    for ID in IDs:
        phenotype = embryos.loc[ID]['phenotype']
        print(func.__name__,phenotype,ID,' ',datetime.now().strftime("%H:%M:%S"),'    ', len(result),'/',len(IDs))
        value = func(phenotype,ID,*args,**kwargs)
        if value is not None:
            result[ID] = value
    return result


def return_dict(func):
    """convert (save) returned variables to a dictionary, when used as a decorator for ``func``

    Parameters
    ----------
    func : function
        the function to decorate

    Returns
    -------
    dict
        ``{'var0':var0, 'var1':var1}``

    Examples
    --------
    When decorated, the following function returns and saves ``{'img':img, 'imr':imr}``::

        @return_dict
        def read_raw(savedir, dir_raw, ID, LabelR, tRes, nEnd):
            ...
            return img, imr


    If func also returns ``savedir``, the function returns ``{'savedir':savedir, 'img':img, 'imr':imr}``, which is then saved the dictionary as ``ID.npy`` at savedir. The last level folder has the same name as ``func``. 
    
    """

    import functools
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # get the names of the returned variables
        import inspect
        lines = inspect.getsource(func).replace(' ','').split('\n')
        lines = list(filter(None, lines))
        vnames = lines[-1][len('return'):].split(',')

        # execute function
        value = func(*args, **kwargs)
        if value is None:
            return
        
        # construct dictionary of the returned variables
        result = dict(zip(vnames,value))

        # save returned result 
        if 'savedir' in result.keys():
            path = result['savedir']
            path[-2] += func.__name__
            np.save(pjoin(path), result)
        return result
    return wrapper

