#!/usr/bin/env python-real

# Copyright 2024 Antonio Carlos da Silva Senra Filho

# Permission is hereby granted, free of charge, to any person obtaining a copy 
# of this software and associated documentation files (the “Software”), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell 
# copies of the Software, and to permit persons to whom the Software is 
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in 
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN 
# THE SOFTWARE.

from types import SimpleNamespace
import os
import sys
from functools import *

try:
    from asltk.asldata import ASLData
    from asltk.reconstruction import MultiTE_ASLMapping
    from asltk.utils.io import load_image, save_image
except ModuleNotFoundError:
    import slicer.util
    slicer.util.pip_install("asltk==0.7.1")
    from asltk.asldata import ASLData
    from asltk.reconstruction import MultiTE_ASLMapping
    from asltk.utils.io import load_image, save_image

import numpy as np
from rich import print


def executeScript(args):
  # The script execution is following the same data and code structure
  # then implemented in the asltk Python library. To check more details about
  # the CLI execution read the official documentation at: 
  # https://asltk.readthedocs.io/en/main/

  # Validate basic inputs first
  if not checkUpParameters(args):
    print(
        'One or more arguments are not well defined. Please, revise the Multi Echo ASL module call.'
    )
    exit(1)

  print('<filter-start>')
  print('<filter-name>Multi Echo ASL Processing</filter-name>')
  print('<filter-comment>Starting Multi Echo ASL computation...</filter-comment>')
  print('</filter-start>')

  print('<filter-progress>0.1</filter-progress>')
  asl_img = load_image(args.asl)
  m0_img = load_image(args.m0)

  print('<filter-progress>0.2</filter-progress>')
  mask_img = np.ones(asl_img[0, 0, :, :, :].shape)
  if args.mask != '':
      mask_img = load_image(args.mask)

  print('<filter-progress>0.3</filter-progress>')
  try:
    te = [float(s) for s in args.te]
    pld = [float(s) for s in args.pld]
    ld = [float(s) for s in args.ld]
  except Exception:
    te = [float(s) for s in str(args.te[0]).split()]
    pld = [float(s) for s in str(args.pld[0]).split()]
    ld = [float(s) for s in str(args.ld[0]).split()]

  numThreads = int(args.numThreads)
  if numThreads == -1:
      numThreads = os.cpu_count()

  smoothMethod = None if args.smoothMethod == 'None' else str(args.smoothMethod).lower()
  if smoothMethod == 'gaussian':
    smoothParameter = {'sigma': float(args.smoothParameter)}
  elif smoothMethod == 'median':
    smoothParameter = {'size': int(args.smoothParameter)}
  else:
    smoothParameter = None

  # Step 2: Show the input information to assist manual conference
  if args.verbose:
    print(' --- Multi Echo ASL Input Data ---')
    print('ASL file path: ' + args.asl)
    print('ASL image dimension: ' + str(asl_img.shape))
    print('Mask file path: ' + args.mask)
    if args.mask != '':
      print('Mask image dimension: ' + str(mask_img.shape))
    else:
      print('No brain mask provided, assuming full-image processing.')
    print('M0 file path: ' + args.m0)
    print('M0 image dimension: ' + str(m0_img.shape))
    print('PLD: ' + str(pld))
    print('LD: ' + str(ld))
    print('TE: ' + str(te))
    print('---- Advanced Options ----')
    print('T2 Blood: ' + str(args.t2b))
    print('T2 GM: ' + str(args.t2gm))
    print('Average M0: ' + str(args.average_m0))
    print('Number of threads: ' + str(numThreads))
    print('Smoothing method: ' + str(smoothMethod))
    print('Smoothing parameter: ' + str(smoothParameter))

  if args.average_m0:
    data = ASLData(
     pcasl=args.asl, m0=args.m0, ld_values=ld, pld_values=pld, te_values=te,
     average_m0=True
     )
  else:
    data = ASLData(
      pcasl=args.asl, m0=args.m0, ld_values=ld, pld_values=pld, te_values=te,
      average_m0=False
      )
  print('<filter-progress>0.5</filter-progress>')
  print('<filter-comment>Computing T blood-GM map...</filter-comment>')
  recon = MultiTE_ASLMapping(data)
  recon.set_brain_mask(mask_img)
  
  # This is the long-running operation
  maps = recon.create_map(
     cores=numThreads,
     smoothing=smoothMethod,
     smoothing_params=smoothParameter)

  print('<filter-progress>0.9</filter-progress>')
  print('<filter-comment>Saving output files...</filter-comment>')
  save_image(maps['t1blgm'], args.out_tblgm)

  print('<filter-progress>1.0</filter-progress>')
  print('<filter-end>')
  print('<filter-name>Multi Echo ASL Processing</filter-name>')
  print('<filter-comment>Processing completed successfully!</filter-comment>')
  print('</filter-end>')

  if args.verbose:
    print('Execution: Multi Echo ASL finished successfully!')


def checkUpParameters(args):
  is_ok = True
  # Check output folder exist (only if provided and not current dir)
  if args.out_folder and args.out_folder != '.' and not os.path.isdir(args.out_folder):
    print(
       f'Output folder path does not exist (path: {args.out_folder}). Please create the folder before executing the script.'
    )
    is_ok = False

  # Check ASL image exist
  if not args.asl or not os.path.isfile(args.asl):
    print(
        f'ASL input file does not exist (file path: {args.asl}). Please check the input file before executing the script.'
    )
    is_ok = False

  # Check M0  image exist
  if not args.m0 or not os.path.isfile(args.m0):
    print(
        f'M0 input file does not exist (file path: {args.m0}). Please check the input file before executing the script.'
    )
    is_ok = False

  # Check if number of threads is valid
  if args.numThreads == 0 or args.numThreads < -1:
    print(
        f'Number of threads must be -1 (to use all available threads) or a positive integer. Current value: {args.numThreads}.'
    )
    is_ok = False
  if args.numThreads > os.cpu_count():
    print(
        f'Number of threads ({args.numThreads}) is higher than the available number of threads ({os.cpu_count()}).'
    )
    is_ok = False

  # Checks the smoothing Method and Parameters
  valid_smooth_methods = ['None', 'Gaussian', 'Median']
  if args.smoothMethod not in valid_smooth_methods:
    print(
        f'Smoothing method "{args.smoothMethod}" is not valid. Please select one of the following methods: {valid_smooth_methods}.'
    )
    is_ok = False
  if args.smoothMethod == 'Gaussian' and args.smoothParameter <= 0:
    print(
        f'For Gaussian smoothing, the smoothing parameter must be a positive number. Current value: {args.smoothParameter}.'
    )
    is_ok = False
  if args.smoothMethod == 'Median' and (args.smoothParameter <= 0 or args.smoothParameter % 2 == 0):
    print(
        f'For Median smoothing, the smoothing parameter must be a positive odd integer. Current value: {args.smoothParameter}.'
    )
    is_ok = False

  return is_ok

# Adding main caller to execute python script inside Slicer


if __name__ == '__main__':
  print(sys.argv)

  # Named-argument parser (supports --flag value pairs)
  def parse_args(argv):
    args_dict = {}
    i = 1
    while i < len(argv):
      if argv[i].startswith('--'):
        key = argv[i][2:]
        if i + 1 < len(argv) and not argv[i + 1].startswith('--'):
          args_dict[key] = argv[i + 1]
          i += 2
        else:
          args_dict[key] = 'true'
          i += 1
      else:
        i += 1
    return args_dict

  def parse_bool(value):
    if isinstance(value, bool):
      return value
    return str(value).lower() in ('true', '1', 'yes')

  parsed = parse_args(sys.argv)

  # Build args namespace from named arguments
  args = SimpleNamespace(
    out_folder=parsed.get('outputFolder', '.'),
    asl=parsed.get('inputASL', ''),
    m0=parsed.get('inputM0', ''),
    mask=parsed.get('brainMask', ''),
    te=parsed.get('echos', '').split(',') if parsed.get('echos') else [],
    pld=parsed.get('pld', '').split(',') if parsed.get('pld') else [],
    ld=parsed.get('ld', '').split(',') if parsed.get('ld') else [],
    out_tblgm=parsed.get('outputVolume', ''),
    t2b=float(parsed.get('t2b', '165.0')),
    t2gm=float(parsed.get('t2gm', '75.0')),
    average_m0=parse_bool(parsed.get('averageM0', 'false')),
    numThreads=int(parsed.get('numThreads', '-1')),
    smoothMethod=parsed.get('smoothMethod', 'None'),
    smoothParameter=float(parsed.get('smoothParameter', '3.0')),
    verbose=True
  )

  executeScript(args)

