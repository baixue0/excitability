#: directory containing input data
dir_data = '/Volumes/extdrive/baixue/data'

#: directory containing output data
dir_out = '/Volumes/extdrive/baixue/out'

from os.path import exists as pexists
def pjoin(lst,createdir=True):
    """Create path from a (nested) list of str

    Parameters
    ----------
    lst : list
        a (nested) list of str

    Returns
    -------
    str

    Examples
    --------
    >>> pjoin([str0, str1])
    str0/str1

    >>> pjoin([[str0, str1], str2])
    str0-str1/str2

    """

    result = []
    for ele in lst:
        if isinstance(ele, list):
            result.append('-'.join(ele))
        else:
            result.append(ele)
    import os
    from os.path import join
    path = join(*result)
    dirname = os.path.dirname(path)
    if createdir:
        if not pexists(dirname):
            os.makedirs(dirname)
    return path

import numpy as np

#: read pickled dictionary
load_dict = lambda path: np.load(path+'.npy',allow_pickle=True).item()

import pandas as pd
directories = pd.read_csv(pjoin([dir_data,'directories.csv'])).set_index('name')['directory']

embryos = pd.read_csv(pjoin([dir_data,'embryos.csv']),skipinitialspace=True,comment='#').set_index('ID')


def iterate(func,embryos,*args,result={},shuffle=True,**kwargs):
    """apply func to each embryo

    This function simplies the code to execute the same function for a list of embryos

    Parameters
    ----------
    func : function
        a function that takes ``phenotype`` and ``ID`` as the first two arguments with additional positional and/or keyword arguments
    embryos : pandas.DataFrame
        each line specifies the ``phenotype`` , ``ID`` and other information about an embryo
    result : dict, optional
        stores the returned value from func
    shuffle : bool
        whether to randomize the order of embryos

    Returns
    -------
    dict
        returned values from func for each embryo

    Examples
    --------
    .. code-block:: python

        def func(phenotype,ID,*args,**kwargs):
            ...
            return value

        iterate(func,embryos)
        # returns {ID1:func(phenotype1,ID1), ID2:func(phenotype2,ID2), ...}

    Note
    ----------
    * ``args`` and ``kwargs`` allows one to pass an unspecified number of arguments to func. 

    * If func returns None, this ID will not be added to the dictionary. 

    * While executing, iterate prints the embryo to be analyzed in real time, so if func fails on one specific embryo, the same exception can be reproduced for debugging.

    * To randomize the order of execution, set shuffle=True. Shuffling speeds up debugging because the embryos are organized by phenotype and func tested using one phenotype are more likely to fail on a different phenotype.


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
    """convert (save) returned variables to a dictionary, when used as a decorator

    Parameters
    ----------
    func : function
        the function to decorate

    Returns
    -------
    dict
        variables returned by the decorated function as a dictionary

    Examples
    --------
    .. code-block:: python

        @return_dict
        def func1(*args):
            ...
            return var0, var1
        dict1 = func1()
        # returns {'var0':var0, 'var1':var1}

        @return_dict
        def func2(savedir,*args):
            ...
            return savedir, var0, var1

        savedir = ['data_output','',ID]
        dict2 = func2(['data_output','',ID])
        # returns ``{'savedir':savedir, 'var0':var0, 'var1':var1}`` 
        # saves the dictionary as 'data_output/func2/ID.npy'
    
    Note
    --------
    Results from different functions can be combined by 
    
    .. code-block:: python

        dict(**dict1,**dict2)

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

