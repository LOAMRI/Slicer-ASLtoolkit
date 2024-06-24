#!/usr/bin/env python-real

# The MIT License (MIT)

# Copyright (c) 2015 Christopher Mark

# Permission is hereby granted, free of charge, to any person obtaining a 
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, 
# and/or sell copies of the Software, and to permit persons to whom the 
# Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in 
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
# DEALINGS IN THE SOFTWARE.

# Script version: 1.0.0
# IMPORTANT NOTE: This script was copied from the original repository: 
# https://github.com/LOAMRI/LOAM-toolkit/tree/main/python-scripts/asl
# New updates are not given automatically, therefore, in case of modifications,
# it is encouraged to provide a pull request in the LOAM group repository.

from types import SimpleNamespace
import os
import sys
from functools import *

import SimpleITK as sitk
import numpy as np
import math
from scipy.optimize import curve_fit


def executeScript(args):
    # The script execution is follwing the same data and code structure
    # then implemented in the LOAM group repository. However, the Argparsers
    # method logic is not used directly due to Slicer scripted CLI model that
    # accepts only direct call in the system command line command.

    # Auxiliary functions

    def build_x_data(ld, pld, te):
        Xdata = np.zeros((len(pld) * len(te), 3)) # array for the x values, assuming an arbitrary size based on the PLD and TE vector size

        count = 0
        for i in range(len(ld)): 
            for j in range(len(pld)):
                Xdata[count] = [ld[i], pld[i], te[j]]
                count += 1     

        return Xdata

    def read_image(image_path: str):
        """Read image from a absolute path and return the Numpy 
        data representation of it.

        Args:
            image_path (str): Absolute image path

        Example:
            img = read_image("path/to/folder/image.nrrd")        

        Return:
            Numpy image format
        """
        img = sitk.ReadImage(image_path)
        return sitk.GetArrayFromImage(img)

    def save_image(image, file_path: str):
        """Save image to a file path.

        Args:
            image (numpy array): Image in numpy array format
            file_path (str): File path defining the absolute path and the file name with the extension.

        Example:
            save_image(np_array, "path/to/folder/image.nii")
        """
        img = sitk.GetImageFromArray(image)
        sitk.WriteImage(img, file_path)

    def asl_model_buxton(tau:list, w:list, m0:float, cbf:float, att:float, 
                        lambda_value:float = 0.98, t1b:float = 1650.0, alpha:float = 0.85):        
        t = np.add(tau, w).tolist()

        t1bp = 1/((1/t1b)+(cbf/lambda_value))
        m_values = np.zeros(len(tau))

        for i in range(0,len(tau)):
            if t[i] < att:
                m_values[i] = 0.0
            elif (att <= t[i]) and (t[i] < tau[i] + att):
                q = 1 - math.exp(-(t[i]-att)/t1bp)
                m_values[i] = 2.0*m0*cbf*t1bp*alpha*q*math.exp(-att/t1b)
            else:
                q = 1 - math.exp(-tau[i]/t1bp)
                m_values[i] = 2.0*m0*cbf*t1bp*alpha*q*math.exp(-att/t1b)*math.exp(-(t[i]-tau[i]-att)/t1bp)

        return m_values


    def asl_model_2compartiments(tau:list, w:list, te:list, m0:float, cbf:float, att:float, t2b:float, t2csf:float, tblcsf:float,
                                alpha:float = 0.85, t1b:float = 1650.0, t1csf:float = 1400.0):

        t1bp = 1/((1/t1b)+(1/tblcsf))
        t1csfp = 1/((1/t1csf)+(1/tblcsf))

        t2bp = 1/((1/t2b)+(1/tblcsf))
        t2csfp = 1/((1/t2csf)+(1/tblcsf))

        t = np.add(tau, w).tolist()

        mag_total = []

        for i in range(0,len(tau)):
            try:
                if t[i] < att:
                    S1b = 0.0
                    S1csf = 0.0
                    if te[i] < (att-t[i]):
                        Sb = 0;
                        Scsf = 0;
                    elif (att - t[i]) <= te[i] and te[i] < (att + tau[i] - t[i]):
                        Sb = 2*alpha*m0*cbf*t2bp*math.exp(-att/t1b)*math.exp(-te[i]/t2b)*(1-math.exp(-(te[i]-att+t[i])/t2bp)) #% measured signal = S2
                        Scsf = 2*alpha*m0*cbf*math.exp(-att/t1b)*math.exp(-te[i]/t2b)*(t2csf*(1-math.exp(-(te[i]-att+t[i])/t2csf))-t2csfp*(1-math.exp(-(te[i]-att+t[i])/t2csfp)))
                    else:
                        Sb = 2*alpha*m0*cbf*t2bp*math.exp(-att/t1b)*math.exp(-te[i]/t2b)*math.exp(-(te[i]-att+t[i])/t2bp)*(math.exp(tau[i]/t2bp)-1)
                        Scsf = 2*alpha*m0*cbf*math.exp(-att/t1b)*math.exp(-te[i]/t2b)*(t2csf*math.exp(-(te[i]-att+t[i])/t2csf)*(math.exp(tau[i]/t2csf)-1)-t2csfp*math.exp(-(te[i]-att+t[i])/t2csfp)*(math.exp(tau[i]/t2csfp)-1))
                elif (att <= t[i]) and (t[i] < (att + tau[i])):
                    S1b = 2*alpha*m0*cbf*t1bp*math.exp(-att/t1b)*(1-math.exp(-(t[i]-att)/t1bp))
                    S1csf = 2*alpha*m0*cbf*math.exp(-att/t1b)*(t1csf*(1-math.exp(-(t[i]-att)/t1csf))-t1csfp*(1-math.exp(-(t[i]-att)/t1csfp)))
                    if te[i] < (att + tau[i] - t[i]):
                        Sb = S1b*math.exp(-te[i]/t2bp) + 2*alpha*m0*cbf*t2bp*math.exp(-att/t1b)*math.exp(-te[i]/t2b)*(1-math.exp(-te[i]/t2bp))
                        Scsf = S1b*(1-math.exp(-te[i]/tblcsf))*math.exp(-te[i]/t2csf) + S1csf*math.exp(-te[i]/t2csf) + 2*alpha*m0*cbf*math.exp(-att/t1b)*math.exp(-te[i]/t2b)*(t2csf*(1-math.exp(-te[i]/t2csf))-t2csfp*(1-math.exp(-te[i]/t2csfp)))
                    else: #% att + tau - t <= te  
                        Sb = S1b*math.exp(-te[i]/t2bp) + 2*alpha*m0*cbf*t2bp*math.exp(-att/t1b)*math.exp(-te[i]/t2b)*math.exp(-te[i]/t2bp)*(math.exp((att+tau[i]-t[i])/t2bp)-1)
                        Scsf = S1b*(1-math.exp(-te[i]/tblcsf))*math.exp(-te[i]/t2csf) + S1csf*math.exp(-te[i]/t2csf) + 2*alpha*m0*cbf*math.exp(-att/t1b)*math.exp(-te[i]/t2b)*(t2csf*math.exp(-te[i]/t2csf)*(math.exp((att+tau[i]-t[i])/t2csf)-1) - t2csfp*math.exp(-te[i]/t2csfp)*(math.exp((att+tau[i]-t[i])/t2csfp)-1))
                else: #% att+tau < t
                    S1b = 2*alpha*m0*cbf*t1bp*math.exp(-att/t1b)*math.exp(-(t[i]-att)/t1bp)*(math.exp(tau[i]/t1bp)-1)
                    S1csf = 2*alpha*m0*cbf*math.exp(-att/t1b)*(t1csf*math.exp(-(t[i]-att)/t1csf)*(math.exp(tau[i]/t1csf)-1) - t1csfp*math.exp(-(t[i]-att)/t1csfp)*(math.exp(tau[i]/t1csfp)-1))
                
                    Sb = S1b*math.exp(-te[i]/t2bp)
                    Scsf = S1b*(1-math.exp(-te[i]/tblcsf))*math.exp(-te[i]/t2csf) + S1csf*math.exp(-te[i]/t2csf)
            except OverflowError:
                Sb = 0.0
                Scsf = 0.0
            
            mag_total.append(Sb+Scsf)

        return mag_total


    # Step 1: Read input data
    asl_img = read_image(args.asl)
    m0_img = read_image(args.m0)

    mask_img = np.ones(asl_img[0, 0, :, :, :].shape)
    if args.mask != "":
        mask_img = read_image(args.mask)


    te= [float(s) for s in args.te]
    pld= [float(s) for s in args.pld]
    ld= [float(s) for s in args.ld]

    # Step 2: Show the input information to assist manual conference
    if args.verbose:
        print(" --- Script Input Data ---")
        print("ASL file path: "+args.asl)
        print("ASL image dimension: "+str(asl_img.shape))
        print("Mask file path: "+args.mask)
        print("Mask image dimension: "+str(mask_img.shape))
        print("M0 file path: "+args.m0)
        print("M0 image dimension: "+str(m0_img.shape))
        print("TE: "+str(te))
        print("PLD: "+str(pld))
        print("LD: "+str(ld))

    # Step 3: Initiate multi-TE PLD ASL processing
    f_map = np.zeros(asl_img[0, 0, :, :, :].shape)
    att_map = np.zeros(asl_img[0, 0, :, :, :].shape)
    Tblgm_map = np.zeros(asl_img[0, 0, :, :, :].shape)


    BuxtonX = [ld, pld] # x data for the Buxton model
    Xdata = build_x_data(ld, pld, te)
    ub = [1.0, 5000.0] # upper limit for the fitting calculation
    lb = [0.0, 0.0] # bottom limit for the fitting calculation
    par0 = [1e-5, 1000] # initial guess for the multiTE-ASL parameters

    # Step 4: Iterate over the image volumes
    y_axis = asl_img.shape[4] # height
    x_axis = asl_img.shape[3] # width
    z_axis = asl_img.shape[2] # depth


    for i in range(x_axis):
        for j in range(y_axis):
            for k in range(z_axis):
                if (mask_img[k, j, i] != 0):
                    m0_px = m0_img[k, j, i]

                    def mod_buxton(Xdata, par1, par2):
                        return asl_model_buxton(Xdata[0], Xdata[1], m0_px, par1, par2)

                    Ydata = asl_img[0,:,k,j,i] # taking the first TE to get less influence in the PLD/Buxton model

                    par_fit, _ = curve_fit(mod_buxton, BuxtonX, Ydata, p0=par0, bounds=(lb, ub))

                    f_map[k, j, i] = par_fit[0] * (60*60*1000) # Applying a normalization factor
                    att_map[k, j, i] = par_fit[1]

                    def mod_2comp(Xdata, par1):
                        return asl_model_2compartiments(Xdata[:,0], Xdata[:,1], Xdata[:,2], m0_px, f_map[k,j,i], att_map[k,j,i],  par1, args.t2b, args.t2gm)

                    Ydata = asl_img[:,:,k,j,i].reshape((len(pld) * len(te), 1)).flatten()

                    par_fit, _ = curve_fit(mod_2comp, Xdata, Ydata, p0=[400.0], bounds=([0.0], [1500.0]))
                    Tblgm_map[k,j,i] = par_fit[0]

    if args.cbf_map:
        save_path=args.out_folder+os.path.sep+"cbf_map.nii.gz"
        if args.verbose:
            print("Saving CBF map - Path: "+save_path)
        save_image(f_map, save_path)

    if args.att_map:
        save_path=args.out_folder+os.path.sep+"att_map.nii.gz"
        if args.verbose:
            print("Saving ATT map - Path: "+save_path)
        save_image(att_map, save_path)

    # save_path=args.out_folder+os.path.sep+"tblgm_map.nii.gz"
    save_path=args.out_tblgm
    if args.verbose:
        print("Saving Tblgm map - Path: "+save_path)
    save_image(Tblgm_map, save_path)

    if args.verbose:
        print("Execution: finished successfully!")

# Adding main caller to execute python script inside Slicer


if __name__ == '__main__':
    print(sys.argv)
    args = SimpleNamespace(
        asl= str(sys.argv[4]),
        m0= str(sys.argv[6]),
        mask= str(sys.argv[8]),
        te= sys.argv[9].split(","),
        pld= sys.argv[10].split(","),
        ld= sys.argv[11].split(","),
        cbf_map= True, # Always save in the output folder
        att_map= True, # Always save in the output folder
        out_folder= str(sys.argv[2]),
        out_tblgm= str(sys.argv[12]),
        t2b= float(sys.argv[13]),
        t2gm= float(sys.argv[14]),
        verbose=True
    )
    
    executeScript(args)

