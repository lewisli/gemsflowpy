import os
import sys

from gemsflowpy.workflows import basic 

grid_name = 'case1'
grid_size = [100,100,25]

porosity_ranges = [[0,0.1],[0.1,0.25],[0.2,0.35]]

perm_means = [0.1,0.2,0.5]
perm_variances = [0.001, 0.005, 0.01]

# Directory to store results in
output_path = 'C:\Users\Lewis Li\Desktop\SampleProject\\'

workflow = basic.porosity_perm_workflow(output_path)
workflow.execute(grid_name,grid_size,porosity_ranges,perm_means,perm_variances)
                    
project_path = 'C:\Users\Lewis Li\Desktop\SampleProject\\'

property_names = ['porosity','perm']
facies_names = ['facies_1','facies_2','facies_3']
depo_real_names = ['real0','real1']
facies_real_names = ['Facies_Real' + str(i) for i in range(10)]

cookies = basic.cookie_cutter(grid_name,grid_size,project_path,property_names,facies_names,depo_real_names,facies_real_names)
cookies._execute()

print 'Workflow Finished!'
