import numpy as np


def num(s):
    '''Convert to an int or a float depending upon string
    '''
    try:
        return int(s)
    except ValueError:
        try:
            return float(s)
        except ValueError: # case when actually is a string
            try: 
                s = s.split(' ')
                s = np.array(s, dtype='|S4')
                s = s.astype(np.float)
                return s
            except ValueError:
                return s


