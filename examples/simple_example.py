import os
import sys

from gemsflowpy.workflows import basic 

grid_name = 'case1'
grid_size = [100,100,25]

facies_names = ['low_qual_sand','high_qual_sand','clay',]

porosity_ranges = [[0.05,0.17],[0.2,0.3],[0.001,0.002],]
perm_means = [110,750,0.001]
perm_variances = [400, 3000,0.00000025]


# Directory to store results in
output_path = 'C:\Users\Lewis Li\Desktop\\Attempt1\\'

num_ti_realizations = 500
ti_workflow = basic.tetris_workflow(output_path)
facies_real_names = ti_workflow.execute(grid_name,grid_size,num_ti_realizations)

# grid_name = 'depositional'
# workflow = basic.porosity_perm_workflow(output_path)
# workflow.execute(grid_name,grid_size,porosity_ranges,perm_means,perm_variances,facies_names)

property_names = ['porosity','perm']
depo_real_names = ['real0']

cookies = basic.cookie_cutter(grid_name,grid_size,output_path,property_names,facies_names,depo_real_names,facies_real_names)
cookies._execute()

print 'Workflow Finished!'
