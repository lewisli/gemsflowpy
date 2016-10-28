import os
import sys

import numpy as np

from gemsflowpy.core import workflow
from gemsflowpy.workflows import internal 
from gemsflowpy.workflows import external


###############################################################################
grid_name = 'SpatialForecasting'
grid_size = [100,100,25]
facies_names = ['low_qual_sand','high_qual_sand','clay']
output_dir = 'C:\Users\Lewis Li\Desktop\\Attempt3\\'
num_ti_realizations = 5
num_depo_real = 1
###############################################################################

###############################################################################
# Part 1: Populate grid with porosity using SGSIM
###############################################################################
prop_name = 'porosity'
# Output distribution for each facies
lq_poro = workflow.trans_parameter(workflow.Uniform,[0.05,0.17])
hq_poro = workflow.trans_parameter(workflow.Uniform,[0.2,0.3])
clay_poro = workflow.trans_parameter(workflow.Uniform,[0.001,0.002])
poro_params = [lq_poro,hq_poro,clay_poro]

poro_modeler = internal.sgsim_workflow(grid_name,grid_size,\
                                       facies_names,prop_name,\
                                       poro_params,\
                                       num_depo_real,output_dir)

poro_output,poro_trans = poro_modeler.execute()


###############################################################################
# Part 2: Populate grid with permability using COSGSIM and clay proportion as
#  		 secondary variable
###############################################################################
prop_name = 'perm'
perm_lq = workflow.trans_parameter(workflow.LogNormal,[110,400])
perm_hq = workflow.trans_parameter(workflow.LogNormal,[750,3000])
perm_clay = workflow.trans_parameter(workflow.LogNormal,[0.001,0.00000025])
perm_params = [perm_lq,perm_hq,perm_clay]

perm_modeler = internal.cosgsim_workflow(grid_name,grid_size,\
                                       facies_names,prop_name,\
                                       perm_params,\
                                       num_depo_real,output_dir)
perm_output,perm_trans = perm_modeler.execute(poro_output)


###############################################################################
# Part 3: Populate grid with facies model using Tetris
###############################################################################
ti_workflow = internal.tetris_workflow(grid_name,grid_size,\
	num_ti_realizations,output_dir)
facies_real_names = ti_workflow.execute()

###############################################################################
# Part 4: Cookie cut each of the realizations together
###############################################################################
cookie_cutter = external.cookie_cut(output_dir,grid_name,grid_size)
cookie_cutter.execute(facies_real_names,facies_names,perm_trans,'perm')
cookie_cutter.execute(facies_real_names,facies_names,poro_trans,'porosity')

print 'Workflow Finished!'
