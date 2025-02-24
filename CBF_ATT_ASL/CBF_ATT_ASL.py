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
    from asltk.reconstruction import CBFMapping
    from asltk.utils import load_image, save_image
except ModuleNotFoundError:
    import slicer.util
    slicer.util.pip_install("asltk>=0.1.4<1.0.0")
    from asltk.asldata import ASLData
    from asltk.reconstruction import CBFMapping
    from asltk.utils import load_image, save_image

import numpy as np
from rich import print


def executeScript(args):
  # The script execution is following the same data and code structure
  # then implemented in the asltk Python library. To check more details about
  # the CLI execution read the official documentation at: 
  # https://asltk.readthedocs.io/en/main/

  asl_img = load_image(args.asl)
  m0_img = load_image(args.m0)

  mask_img = np.ones(asl_img[0, 0, :, :, :].shape)
  if args.mask != '':
      mask_img = load_image(args.mask)

  try:
      pld = [float(s) for s in args.pld]
      ld = [float(s) for s in args.ld]
  except:
      pld = [float(s) for s in str(args.pld[0]).split()]
      ld = [float(s) for s in str(args.ld[0]).split()]

  if not checkUpParameters():
    print(
        'One or more arguments are not well defined. Please, revise the CBF/ATT ASL module call.'
    )
    exit(1)


  # Step 2: Show the input information to assist manual conference
  if args.verbose:
    print(' --- CBF/ATT ASL Input Data ---')
    print('ASL file path: ' + args.asl)
    print('ASL image dimension: ' + str(asl_img.shape))
    print('Mask file path: ' + args.mask)
    print('Mask image dimension: ' + str(mask_img.shape))
    print('M0 file path: ' + args.m0)
    print('M0 image dimension: ' + str(m0_img.shape))
    print('PLD: ' + str(pld))
    print('LD: ' + str(ld))

  data = ASLData(pcasl=args.asl, m0=args.m0, ld_values=ld, pld_values=pld)
  recon = CBFMapping(data)
  recon.set_brain_mask(mask_img)
  maps = recon.create_map()

  if args.norm_cbf:
    save_image(maps['cbf_norm'], args.out_cbf)
  else:
    save_image(maps['cbf'], args.out_cbf)
  save_image(maps['att'], args.out_att)

  if args.verbose:
    print('Execution: CBF/ATT ASL finished successfully!')


def checkUpParameters():
  is_ok = True
  # Check output folder exist
  if not (os.path.isdir(args.out_folder)):
    print(
       f'Output folder path does not exist (path: {args.out_folder}). Please create the folder before executing the script.'
    )
    is_ok = False

  # Check ASL image exist
  if not (os.path.isfile(args.asl)):
    print(
        f'ASL input file does not exist (file path: {args.asl}). Please check the input file before executing the script.'
    )
    is_ok = False

  # Check M0  image exist
  if not (os.path.isfile(args.m0)):
    print(
        f'M0 input file does not exist (file path: {args.m0}). Please check the input file before executing the script.'
    )
    is_ok = False

  return is_ok

# Adding main caller to execute python script inside Slicer
if __name__ == '__main__':
    print(sys.argv)
    args = SimpleNamespace(
        asl= str(sys.argv[4]),
        m0= str(sys.argv[6]),
        mask= str(sys.argv[8]),
        pld= sys.argv[9].split(","),
        ld= sys.argv[10].split(","),
        out_folder= str(sys.argv[2]),
        out_cbf= str(sys.argv[11]),
        norm_cbf=bool(sys.argv[12]),
        out_att= str(sys.argv[13]),
        verbose=True
    )
    
    executeScript(args)

