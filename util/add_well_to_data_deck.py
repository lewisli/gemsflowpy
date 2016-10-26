#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 25 16:37:52 2016

@author: lewisli
"""
import scipy.io as sio
import os
import numpy as np

# Well Locations
well_location_path = '/Volumes/Scratch2/Data/SpatialForecasting/Case2/processed/WellLocations.mat'

mat_contents = sio.loadmat(well_location_path)
locations={}
locations['Prior']= mat_contents['PriorLocations']
locations['Posterior']=mat_contents['PosteriorLocations']

#num_prior_runs = prior_locations.shape[0]
#num_post_runs = post_locations.shape[0]

output_dir = '/Volumes/Scratch2/Data/SpatialForecasting/Case2WellLocations/'

# Base data file path
base_deck_path = output_dir + 'Truth/Run392.dat'
with open(base_deck_path) as f:
    basecase = f.read().splitlines()

# Find the line where 'END WELLS' is written and add a new well
sub = 'NAME=PNEW TYPE=P I= 44 J= 61 K=1-25 DIA=0.50 SKIN=0 DIR=Z'
matching=filter(lambda x: sub in x, basecase)


for case in locations:
    case_dir = output_dir + case + '/'
    num_runs = locations[case].shape[0]

    for well_no in range(0,num_runs):
        run_folder_path = case_dir + 'Run' + str(well_no) + '/'
        run_file_path = run_folder_path + 'Run'+str(well_no)+'.dat'
        
        # make copy of basecase
        new_case = list(basecase)
        
        # make a folder for each run
        if not os.path.exists(run_folder_path):
            os.makedirs(run_folder_path)
            
        out_file = open(run_file_path,'w')
    
        # String that describes location of new well
        well_str_loc = 'NAME=PNEW TYPE=P I= ' + str(locations[case][well_no,0]) + \
            ' J= ' + str(locations[case][well_no,1]) + ' K=1-25 DIA=0.50 SKIN=0 DIR=Z'
        new_case[basecase.index(sub)] = well_str_loc
        out_file.write("\n".join(new_case))
        
        out_file.close()

