import os
import sys

from gemsflowpy.workflows import basic 

grid_name = 'ClayCase'
grid_size = [100,100,1]

# Fine, medium and coarse sand
facies_names = ['fs','ms','cs',]

# Clay
clay_means = [0.24,0.13,0.04]
clay_variances = [0.05,0.05,0.001]

# Directory to store results in
output_path = 'C:\Users\Lewis Li\Desktop\\Attempt1\\'

grid_name = 'clay'
num_realizations = 1
workflow = basic.porosity_perm_workflow(output_path)
workflow.execute(grid_name,grid_size,clay_means,clay_variances,facies_names,num_realizations)


print 'Workflow Finished!'
