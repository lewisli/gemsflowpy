import os
import sys

from gemsflowpy.workflows import basic 

grid_name = 'case1'
grid_size = [100,100,25]
porosity_ranges = [[0,0.1],[0.1,0.25],[0.2,0.35]]
perm_means = [0.3,0.5,0.6]

workflow = basic.porosity_perm_workflow()
workflow.execute(grid_name,grid_size,porosity_ranges,perm_means)

