import numpy as np
from utils.path_io import pjoin

def iterate(func,embryos,*args,result={},shuffle=True,**kwargs):
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


def repeat(embryos,result,shuffle=True):
    '''
    use as decorator (nested decorator)
    run the decorated function "func" for each value in IDs and save the return of "func" in "result" as a dictionary
    '''
    IDs = list(embryos.index.copy())
    if shuffle:
        import random
        random.shuffle(IDs)
    def decorator_repeat(func):
        import functools
        @functools.wraps(func)
        def wrapper_repeat(*args, **kwargs):
            from datetime import datetime
            for ID in IDs:
                phenotype = embryos.loc[ID]['phenotype']
                print(func.__name__,phenotype,ID,' ',datetime.now().strftime("%H:%M:%S"),'    ', len(result),'/',len(IDs))
                value = func(phenotype,ID,*args, **kwargs)
                if value is not None:
                    result[ID] = value
        return wrapper_repeat
    return decorator_repeat

def return_dict(func):
    '''
    use as decorator for "func"
    return variables as dictionary
    save dictionary as .npy if func returns "save"
    '''
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
        if 'save' in result.keys():
            path = result['save']
            path[-2] += func.__name__
            np.save(pjoin(path), result)
        return result
    return wrapper

