import numpy as np


def fread(f, dtype, count):
  '''
  '''
  if dtype == 'nchar':
    nchar = np.fromfile(f, dtype='<i1', count=1)
    if nchar == 0:
      raise InputValue(' *** Expecting char value > 0\n')

    f.read(3) # skip over whit space
    val = f.read(nchar) # read in value

  elif dtype == 'char':
    val = f.read(1)

  elif dtype == 'int':
    val = np.fromfile(f, dtype='<i4', count=count)

  elif dtype == 'float':
    val = np.fromfile(f, dtype='<f4', count=count) # 32 bit float

  return val


def nd_read(infile):
  '''nd_read(infile)

    The python functions below will read an nData file 
    (binary format) into a dictionary.

    For documentation,  go to:  www.iModel.org/nd/  and click on the
      "python format" link on the left.

    NOTES
      (1) ian is not checked.
      (2) Event code table is not handled.
  '''

  fin = open(infile, 'r')
    
  #  Read the first [int],  if it is not 1,  change ian.
  tval = fread(fin, 'int', 1)
  if (tval != 1):
    raise IOError('Cannot read file - possible ian problem. Exiting\n')

  nd = {} # create dictionary for data
  #
  #  Read the file class,  which is a string describing the file
  #
  nd['class'] = fread(fin, 'nchar', 1)
  print('    File class:  {0}\n'.format(nd['class']))

  #
  #  Read the constant parameters
  #
  nd['nconst'] = fread(fin, 'int', 1)  # Number of constant parameters
  print('    Constant parameters:  {0}\n'.format(nd['nconst']))

  nd['const'] = {}
  for i in range(0, nd['nconst']):
    name = fread(fin, 'nchar', 1)
    nd['const'][name] = {}
    nd['const'][name]['type'] = fread(fin, 'char', 1)
    nd['const'][name]['val']  = fread(fin, 'nchar', 1) 

  #
  #  Read names and types of variable parameters
  #
  nd['nvar'] = fread(fin, 'int', 1)  # Number of variable parameters
  print('    Variable parameters:  {0}\n'.format(nd['nvar']))
  if (nd['nvar'] > 0):
    print('     ')
  
  nd['var'] = {}
  for i in range(0, nd['nvar']):
    nd['var'][i] = {}
    nd['var'][i]['name'] = fread(fin, 'nchar', 1)
    nd['var'][i]['type'] = fread(fin, 'char', 1)
    print('\t {0}'.format(nd['var'][i]['name']))

  print('\n')

  #
  #  Read the event code table
  #
  nd['ntable'] = fread(fin, 'int', 1)  # Number of event-code tables
  if nd['ntable'] > 0:
    raise IOError('  *** This feature not available:  event code tables\n')

  #
  #  Read the number of trials
  #
  nd['ntrial'] = fread(fin, 'int', 1)  # Number of trials
  print('    Trials:  {0}\n'.format(nd['ntrial']))
  
  nd['tr'] = {}
  for i in range(0, nd['ntrial']):
    #
    #  Read the header information for this trial
    #
    nd['tr'][i] = {}
    nd['tr'][i]['tcode']  = fread(fin, 'int', 1)
    nd['tr'][i]['tref']   = fread(fin, 'int', 1)
    nd['tr'][i]['nparam'] = fread(fin, 'int', 1) # Number of variable params

    for j in range(0, nd['tr'][i]['nparam']):
      nd['tr'][i]['par'] = {}
      nd['tr'][i]['par']['name'] = fread(fin, 'nchar', 1)
      nd['tr'][i]['par']['val']  = fread(fin, 'nchar', 1)
  
    nd['tr'][i]['nrec'] = fread(fin, 'int', 1) # Number of records (aka channels)

    nd['tr'][i]['r'] = {}
    for j in range(0, nd['tr'][i]['nrec']):
      nd['tr'][i]['r'][j] = {}
      nd['tr'][i]['r'][j]['rtype'] = fread(fin, 'int', 1)
      nd['tr'][i]['r'][j]['name'] = fread(fin, 'nchar', 1)
      nd['tr'][i]['r'][j]['rcode'] = fread(fin, 'int', 1)
      nd['tr'][i]['r'][j]['sampling'] = fread(fin, 'float', 1)
      nd['tr'][i]['r'][j]['t0'] = fread(fin, 'int', 1)
      nd['tr'][i]['r'][j]['tn'] = fread(fin, 'int', 1)
      nd['tr'][i]['r'][j]['n'] = fread(fin, 'int', 1)

      # read the raw data
      if nd['tr'][i]['r'][j]['rtype'] == 0:
        nd['tr'][i]['r'][j]['p'] = fread(fin, 'int', nd['tr'][i]['r'][j]['n'])

      elif nd['tr'][i]['r'][j]['rtype'] == 1:
        nd['tr'][i]['r'][j]['x'] = fread(fin, 'float', nd['tr'][i]['r'][j]['tn'])

      elif nd['tr'][i]['r'][j]['rtype'] == 2:
        for k in range(0, nd['tr'][i]['p'][j]['n']):
          nd['tr'][i]['r'][j]['p'] = fread(fin, 'int', nd['tr'][i]['r'][j]['n'])
          nd['tr'][i]['r'][j]['x'] = fread(fin, 'float', 
                                           nd['tr'][i]['r'][j]['tn'])

      else:
        raise IOError('  *** Feature not implemented yet:  rtype > 2\n')

  fin.close()

  return nd
  

if __name__ == '__main__':

    nd = nd_read('zz.nd')
