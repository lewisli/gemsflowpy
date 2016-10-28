# -*- coding: utf-8 -*-
"""
Created on Thu Oct 27 23:08:29 2016

@author: Lewis Li
"""

import numpy as np

from gemsflowpy.core import workflow
from gemsflowpy.workflows import internal 
from gemsflowpy.workflows import external

grid_name = 'ClayCase'
grid_size = [101,101,1]
facies_names = ['fs','ms','cs']
output_dir = 'C:\Users\Lewis Li\Desktop\Attempt2\\'

num_real = 2

###############################################################################
# Part 1: Populate grid with clay percentage using SGSIM
###############################################################################
prop_name = 'clay_percentage'
# Output distribution for each facies
clay_fs = workflow.trans_parameter(workflow.Uniform,[0.18,0.29])
clay_ms = workflow.trans_parameter(workflow.Uniform,[0.08,0.18])
clay_cs = workflow.trans_parameter(workflow.Uniform,[0.00004,0.08])
clay_params = [clay_fs,clay_ms,clay_cs]

clay_modeler = internal.sgsim_workflow(grid_name,grid_size,\
                                       facies_names,prop_name,\
                                       clay_params,\
                                       num_real,output_dir)
clay_output,clay_trans = clay_modeler.execute()


###############################################################################
# Part 2: Populate grid with permability using COSGSIM and clay proportion as
#  		 secondary variable
###############################################################################
prop_name = 'perm'
perm_fs = workflow.trans_parameter(workflow.Gaussian,[50,5])
perm_ms = workflow.trans_parameter(workflow.Gaussian,[100,5])
perm_cs = workflow.trans_parameter(workflow.Gaussian,[200,5])
perm_params = [perm_fs,perm_ms,perm_cs]

perm_modeler = internal.cosgsim_workflow(grid_name,grid_size,\
                                       facies_names,prop_name,\
                                       perm_params,\
                                       num_real,output_dir)
perm_output,perm_trans = perm_modeler.execute(clay_output)

###############################################################################
# Part 3: Populate grid with porosity using LinearTrans and clay proportion as
#     	 dependent variable
###############################################################################
prop_name = 'porosity'
a = -0.875
b = 0.35
clay_porosity_modeler = external.linear_transformation(output_dir,grid_name,grid_size)
clay_poro_names = clay_porosity_modeler.execute(clay_trans,prop_name,a,b,)

###############################################################################
# Part 4: Populate grid with cev using LinearTrans and clay proportion as
#         dependent variable
###############################################################################
prop_name = 'cec'
a = 628.58
b = 48.863
cecmodel = external.linear_transformation(output_dir,grid_name,grid_size)
clay_cec_names = cecmodel.execute(clay_trans,prop_name,a,b,)

###############################################################################
# Part 5: Populate grid with facies model using Tetris
###############################################################################
num_ti_realizations = 5
ti_workflow = internal.tetris_workflow(grid_name,grid_size,\
	num_ti_realizations,output_dir)
facies_real_names = ti_workflow.execute()

###############################################################################
# Part 6: Cookie cut each of the realizations together
###############################################################################
cookie_cutter = external.cookie_cut(output_dir,grid_name,grid_size)
cookie_cutter.execute(facies_real_names,facies_names,perm_trans,'perm')
cookie_cutter.execute(facies_real_names,facies_names,clay_poro_names,'porosity')
cookie_cutter.execute(facies_real_names,facies_names,clay_cec_names,'cec')

print 'Workflow done'