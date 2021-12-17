#: directory containing input data
dir_data = '/Volumes/extdrive/baixue/data'

#: directory containing output data
dir_out = '/Volumes/extdrive/baixue/out'

from os.path import exists as pexists
def pjoin(lst,createdir=True):
    '''
    Create path from a (nested) list of str

    :param lst: a (nested) list of str
    :type lst: list
    :rtype: str

    Example::

        >>> pjoin([str0, str1])
        str0/str1

        >>> pjoin([[str0, str1], str2])
        str0-str1/str2
    '''
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
