

def num(s):
    '''Convert to an int or a float depending upon string
    '''
    try:
        return int(s)
    except ValueError:
        try:
            return float(s)
        except ValueError: # case when actually is a string
            return s


