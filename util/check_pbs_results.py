# -*- coding: utf-8 -*-
"""
Created on Fri Oct 14 14:34:12 2016

@author: lewisli
"""

from os import listdir
from os.path import isfile, join


#%% Check which runs failed because of cluster killing all jobs that exceed
# 2 hours

def check_pbs_results(project_dir): 
    log_dir = project_dir + 'Logs/'
    
    onlyfiles = [f for f in listdir(log_dir) if isfile(join(log_dir, f))]
    problem_files = []

    for files in onlyfiles:
        if 'Terminated due to Ctrl-C/Kill request' in open(log_dir+files).read():
            problem_files.append(files)
            print files

    return problem_files