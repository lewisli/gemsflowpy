import sys
import os
import itertools
import numpy as np
from gemsflowpy.core import workflow


class linear_transformation(workflow.python_workflow):
    def __init__(self,output_dir,grid_name,grid_size):
        super(linear_transformation, self).__init__(output_dir,grid_name,grid_size)
        
    def execute(self,facies_names,prop_name,a,b):
        output_names = dict()

        # Iterate over each facies
        for facies_name, facies_reals in facies_names.iteritems():
            depo_real_names = []
            # Iterate over each realization in facies 
            for facies in facies_reals:
                facies_path = self.output_dir + '/Properties//' + facies
                
                input_values = self.read_sgems_files(facies_path)
                
                transformed_values = input_values*(a) + b
    
                transformed_name = facies + '_' + prop_name
                depo_real_names.append(transformed_name)
                
                output_path = self.output_dir + '/Properties//' +  \
                    transformed_name
                
                # output porosity file
                output_fid = open(output_path,'w');
    
                output_fid.write(self.grid_name + '(' + 'x'.join(str(dim) \
                    for dim in self.grid_size) + ')\n')
                output_fid.write(str(1)+'\n')
                output_fid.write(prop_name+'\n')
                
                for index, x in np.ndenumerate(transformed_values):
                    output_fid.write(str(max(x,0)) + '\n')
                    
                output_fid.close()

            output_names[facies_name] = depo_real_names
            
        return output_names  

class cookie_cut(workflow.python_workflow):
    def __init__(self,output_dir,grid_name,grid_size):
        super(cookie_cut, self).__init__(output_dir,grid_name,grid_size)

    def execute(self,facies_reals,facies_names,depositional_reals,prop_name):
        # facies_reals is a list of the facies_map realization
        # depositional_reals is a dictionary where the key is the facies name
        # and each value is a list of output variables

        # Folder where depositional properties are stored
        self.prop_dir = self.output_dir +'Properties\\' 

        # Folder where facies maps are stored
        self.facies_dir = self.output_dir + 'Facies\\'

        # Folder to store output realizations
        self.output_path = self.output_dir + 'Realizations\\'

        # Make output directories
        for path in [self.prop_dir,self.facies_dir,self.output_path]:
            if not os.path.exists(path):
                os.makedirs(path)

        num_header_lines = 3

        depo_values = dict()

        # Load depositional realizations into memory
        for facies_name,depo_reals in depositional_reals.iteritems():
            depo_list = []
            for d_num,depo_real in enumerate(depo_reals):
                depo_path = self.prop_dir + depo_real

                prop_fid = open(depo_path)
                depo_list.append(prop_fid.readlines()[num_header_lines:])

                self.num_depo_reals = d_num + 1
            depo_values[facies_name] = depo_list



        # Iterate over each facies realization
        for facies_real in facies_reals:

            # Path at which facies map has been stored
            facies_path = self.facies_dir+facies_real+'.sgems'

            # Iterate over depositional realizations
            for output_real_no in range(0,self.num_depo_reals):
                
                # Path to store output realizations
                output_name = facies_real + '_' + prop_name + '_real_' + \
                    str(output_real_no) 
                output_path = self.output_path + output_name + '.sgems'
                output_fid = open(output_path,'w');

                output_fid.write(self.grid_name + '(' + 'x'.\
                            join(str(dim) for dim in self.grid_size) + ')\n')
                output_fid.write(str(1)+'\n')
                output_fid.write(output_name+'\n')

                # read in facies map
                with open(facies_path, "r") as facies_grid:
                    # Skip first 3 lines of facies_grid
                    for _ in xrange(num_header_lines):
                        next(facies_grid)

                    # Iterate over each line in facies_grid and look up
                    # corresponding depositional variable
                    for line,facies in enumerate(facies_grid):
                        current_facies = facies_names[int(facies)]
                        output_fid.write(depo_values[current_facies]\
                            [output_real_no][line])

                    output_fid.close()
                facies_grid.close()


        
