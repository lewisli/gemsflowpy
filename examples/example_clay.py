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
output_path = 'C:\Users\Markus Zechner\Desktop\FirstTrialClay\\'

grid_name = 'clay'
num_realizations = 1
workflow = basic.clay_modeling_workflow(output_path)
workflow.execute(grid_name,grid_size,clay_means,clay_variances,facies_names,num_realizations)

file_name = '/Users/lewisli/Documents/Scratch/Properties/cs_clay_dist_real0'
input_folder = '/Users/lewisli/Documents/Scratch/Properties/'
porositymodel = basic.clay_porosity_workflow(input_folder)
facies_names = ['cs_clay_dist_real0']
grid_size = [100,100,1]
grid_name = 'clay'
test_input = porositymodel.execute(input_folder,facies_names,grid_name,grid_size)


cecmodel = basic.clay_cec_workflow(input_folder)
cecmodel.execute(input_folder,facies_names,grid_name,grid_size)


print 'Workflow Finished!'
