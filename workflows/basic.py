import sys
import os
import itertools
import numpy as np
from gemsflowpy.core import workflow


class cookie_cutter(object):
    """ Implementation of "cookie-cutter" algorithm

    Attributes:
        prop_dir(str): Path where properties for each facies are stored
        prop_names(str): Name of properties file
        facies_maps(str): Path to where facies map(s) are stored
        num_facies(int): 
    """
    
    def __init__(self,grid_name,grid_size,project_path,prop_names,facies_names,real_names,facies_real_names):

        # Folder where depositional properties are stored
        self.prop_dir = project_path +'Properties\\' 

        # Folder where facies maps are stored
        self.facies_dir = project_path + 'Facies\\'

        # Folder to store output realizations
        self.output_path = project_path + 'Realizations\\'

        # make directories
        for path in [self.prop_dir,self.facies_dir,self.output_path]:
            if not os.path.exists(path):
                os.makedirs(path)

        self.grid_name = grid_name
        self.grid_size = grid_size


        # Name of properties (ex: PermX,PermY,Porosity)
        self.prop_names = prop_names

        # Name of realizations (ex: Real0,Real1, or Low, Mid High )
        self.real_names = real_names

        # Name of facies (ex: Facies_1, Shale, Sand-Mix, etc)
        self.facies_names = facies_names\

        self.facies_real_names = facies_real_names
        
        
    def _execute(self):

        num_header_lines = 3

        # Perform for each property type
        for prop_type in self.prop_names:
            for real in self.real_names:
            
                prop_list = []
                for facies_name in self.facies_names:
                    print facies_name
                    # Iterate over properties
                    prop_name = '_'.join([facies_name,prop_type,real])
                    
                    # Read each depositional property file
                    prop_fid = open(self.prop_dir + prop_name)
                    prop_list.append(prop_fid.readlines()[num_header_lines:])
                    

                # Iterate over each MPS realization
                for facies_map in self.facies_real_names:

                    facies_path = self.facies_dir+facies_map+'.sgems'
                    output_name = facies_map + '_' + prop_type + '_depo_' + str(real)
                    output_path = self.output_path + output_name + '.sgems'

                    output_fid = open(output_path,'w');

                    with open(facies_path, "r") as facies_grid:
                        # Skip first 3 lines of facies_grid
                        for _ in xrange(num_header_lines):
                            next(facies_grid)

                        output_fid.write(self.grid_name + '(' + 'x'.join(str(dim) for dim in self.grid_size) + ')\n')
                        output_fid.write(str(1)+'\n')
                        output_fid.write(output_name+'\n')

                        for line,facies in enumerate(facies_grid):
                            output_fid.write(prop_list[int(facies)][line])

                    output_fid.close()


class tetris_workflow(workflow.sgems_workflow):
    def __init__(self,output_dir):
        super(tetris_workflow, self).__init__(output_dir)

    def execute(self,grid_name,grid_size,num_realizations=10):

        num_facies_map = num_realizations
        
        # Step 1: Create an empty grid of size(100,100,25)
        self.create_grid(grid_name,grid_size)        

        # Generate training image realizations
        self.available_algo['TetrisTiGen'].reset()
        self.available_algo['TetrisTiGen'].update_parameter(['Grid'],'value',grid_name)
        self.available_algo['TetrisTiGen'].update_parameter(['Property'],'value','Facies_map')
        self.available_algo['TetrisTiGen'].update_parameter(['Nb_Realizations'],'value',str(num_facies_map))

        facies_map_names = self.run_geostat_algo('TetrisTiGen')

        for facies_map in facies_map_names:

            output_obj_path = 'Facies\\' + facies_map + '.sgems'
            self.save_grid(grid_name,facies_map,output_obj_path)

        return facies_map_names


class clay_modeling_workflow(workflow.sgems_workflow):
    def __init__(self,output_dir):
        super(clay_modeling_workflow, self).__init__(output_dir)

    def execute(self,grid_name,grid_size,clay_mean,clay_variance,facies_names,num_realizations):

        # Step 1: Create a grid
        self.create_grid(grid_name,grid_size)

        # Step 2: Generate SGSIM Realization for the facies
        for f,(mean,var,facies_name) in enumerate(zip(clay_mean,clay_variance,facies_names)):
                self.available_algo['sgsim'].reset()
                self.available_algo['sgsim'].update_parameter(['Grid_Name'],\
                    'value',grid_name)
                self.available_algo['sgsim'].update_parameter(['Property_Name'],\
                    'value',facies_name+'_clay_dist')
                    
                # Set number of realizations
                self.available_algo['sgsim'].update_parameter(['Nb_Realizations'],\
                    'value',str(num_realizations))

                 # Get clay realization names
                clay_raw_names = self.run_geostat_algo('sgsim')
                if type(clay_raw_names) is str:
                    clay_raw_names = [clay_raw_names]


                # Part 4: Transform clay to Gaussian
                clay_trans_names = []
                self.available_algo['trans'].reset()

                self.available_algo['trans'].update_parameter(['grid'],\
                    'value',grid_name)
                self.available_algo['trans'].update_parameter(['props'],\
                    'count',str(num_realizations))
                self.available_algo['trans'].update_parameter(\
                    ['Use_break_tie_index'],'value','0')
                self.available_algo['trans'].update_parameter(\
                    ['ref_type_target'],'value','Gaussian')
                self.available_algo['trans'].update_parameter(\
                    ['G_mean_target'],'value',str(mean))
                self.available_algo['trans'].update_parameter(\
                    ['G_variance_target'],'value',str(var))
                self.available_algo['trans'].update_parameter(\
                    ['props'],'value',';'.join(clay_raw_names))
                
                clay_trans_names = self.run_geostat_algo(\
                        'trans')

                output_obj_names = []
                for i in range(0,num_realizations):

                    output_obj_name = 'Properties\\'+facies_name+'_clay_dist_real'+str(i) 
                    output_obj_names.append(output_obj_name)
                            
                    if num_realizations == 1:
                        self.save_grid(grid_name,str(clay_trans_names),\
                                output_obj_name)
                    else:
                        self.save_grid(grid_name,clay_trans_names[i],\
                                output_obj_name)

class python_workflow(object):
    def __init__(self,output_dir):
        self.output_dir = output_dir

    def read_sgems_files(self,file_name):
        num_header_lines = 3

        raw_input = np.genfromtxt(file_name,skip_header=num_header_lines)

        return raw_input
        
class clay_porosity_workflow(python_workflow):
    def __init__(self,output_dir):
        super(clay_porosity_workflow, self).__init__(output_dir)
        
        
    def execute(self,input_dir,facies_names,grid_name,grid_size):
        for facies in facies_names:
            facies_path = input_dir + '/' + facies
            
            clay_input = self.read_sgems_files(facies_path)
            
            output_porosity = clay_input*(-0.875) + 0.35

            porosity_name = facies + '_porosity'
            
            porosity_path = self.output_dir + porosity_name
            
            # output porosity file
            output_fid = open(porosity_path,'w');

            output_fid.write(grid_name + '(' + 'x'.join(str(dim) for dim in grid_size) + ')\n')
            output_fid.write(str(1)+'\n')
            output_fid.write(porosity_name+'\n')
            
            for index, x in np.ndenumerate(output_porosity):
                output_fid.write(str(x) + '\n')
                
            output_fid.close()
            
        
class clay_cec_workflow(python_workflow):
    def __init__(self,output_dir):
        super(clay_cec_workflow, self).__init__(output_dir)
        
        
    def execute(self,input_dir,facies_names,grid_name,grid_size):
        for facies in facies_names:
            facies_path = input_dir + '/' + facies
            
            clay_input = self.read_sgems_files(facies_path)
            
            output_cec = clay_input*(628.58) + 48.863

            cec_name = facies + '_cec'
            
            cec_path = self.output_dir + cec_name
            
            # output porosity file
            output_fid = open(cec_path,'w');

            output_fid.write(grid_name + '(' + 'x'.join(str(dim) for dim in grid_size) + ')\n')
            output_fid.write(str(1)+'\n')
            output_fid.write(cec_name+'\n')
            
            for index, x in np.ndenumerate(output_cec):
                output_fid.write(str(x) + '\n')
                
            output_fid.close()
        
        


class porosity_perm_workflow(workflow.sgems_workflow):
    def __init__(self,output_dir):
        super(porosity_perm_workflow, self).__init__(output_dir)

    def execute(self,grid_name,grid_size,porosity_ranges,perm_means,perm_variances,facies_names):

        # Step 1: Create an empty grid of size(100,100,25)
        self.create_grid(grid_name,grid_size)        
        
        # Grid Parameters
        num_realizations = 1
        
        for f,(poro_range,perm_mean,perm_var,facies_name) in enumerate(zip(porosity_ranges,\
            perm_means,perm_variances,facies_names)):
                
                # Part 2: Generate porosity realizations
                self.available_algo['sgsim'].reset()
                self.available_algo['sgsim'].update_parameter(['Grid_Name'],\
                    'value',grid_name)
                self.available_algo['sgsim'].update_parameter(['Property_Name'],\
                    'value',facies_name+'_porosity')
                    
                # Set number of realizations
                self.available_algo['sgsim'].update_parameter(['Nb_Realizations'],\
                    'value',str(num_realizations))
                    
                # Get porosity realization names
                porosity_raw_names = self.run_geostat_algo('sgsim')
                if type(porosity_raw_names) is str:
                    porosity_raw_names = [porosity_raw_names]

                # Part 2: Generate permability realizations
                permeability_raw_names = []
                for i in range(0,num_realizations):
                    self.available_algo['colocated-sgsim'].update_parameter(\
                        ['Grid_Name'],'value',grid_name)
                    self.available_algo['colocated-sgsim'].update_parameter(\
                        ['Secondary_property'],'value',porosity_raw_names[i])
                    self.available_algo['colocated-sgsim'].update_parameter(\
                        ['Property_Name'],'value',facies_name+\
                        '_perm'+'_real_' + str(i))
                    
                    # Get perm names
                    permeability_raw_names.append(self.run_geostat_algo(\
                        'colocated-sgsim'))
                

                        
                # Part 3: Transform Porosities to uniform distribution
                porosity_trans_names = []
                self.available_algo['trans'].reset()
                self.available_algo['trans'].update_parameter(['grid'],\
                    'value',grid_name)
                self.available_algo['trans'].update_parameter(\
                    ['Use_break_tie_index'],'value','0')
                self.available_algo['trans'].update_parameter(['props'],\
                    'count',str(num_realizations))
                self.available_algo['trans'].update_parameter(\
                    ['props'],'value',';'.join(porosity_raw_names))
                self.available_algo['trans'].update_parameter(\
                    ['ref_type_target'],'value','Uniform')
                self.available_algo['trans'].update_parameter(\
                    ['Unif_min_target'],'value',str(poro_range[0]))
                self.available_algo['trans'].update_parameter(\
                    ['Unif_max_target'],'value',str(poro_range[1]))

                porosity_trans_names = self.run_geostat_algo(\
                        'trans')

                output_obj_names = []
                
                # Part 4: Transform permabilities to log-normal
                perm_trans_names = []
                self.available_algo['trans'].reset()
                self.available_algo['trans'].update_parameter(['grid'],\
                    'value',grid_name)
                self.available_algo['trans'].update_parameter(['props'],\
                    'count',str(num_realizations))
                self.available_algo['trans'].update_parameter(\
                    ['Use_break_tie_index'],'value','0')
                self.available_algo['trans'].update_parameter(\
                    ['ref_type_target'],'value','Log Normal')
                self.available_algo['trans'].update_parameter(\
                    ['LN_mean_target'],'value',str(perm_mean))
                self.available_algo['trans'].update_parameter(\
                    ['LN_variance_target'],'value',str(perm_var))
                self.available_algo['trans'].update_parameter(\
                    ['props'],'value',';'.join(permeability_raw_names))
                
                perm_trans_names = self.run_geostat_algo(\
                        'trans')

                # TODO: Clean up this shit
                for i in range(0,num_realizations):
                    output_obj_name = 'Properties\\'+facies_name+'_porosity_real'+str(i) 
                    output_obj_names.append(output_obj_name)
                    
                    if num_realizations == 1:
                        self.save_grid(grid_name,str(porosity_trans_names),\
                            output_obj_name)
                    else:
                        self.save_grid(grid_name,porosity_trans_names[i],\
                            output_obj_name)

                    output_obj_name = 'Properties\\'+facies_name+'_perm_real'+ str(i) 
                    output_obj_names.append(output_obj_name)
                    
                    if num_realizations == 1:
                        self.save_grid(grid_name,str(perm_trans_names),\
                            output_obj_name)
                    else:
                        self.save_grid(grid_name,perm_trans_names[i],\
                            output_obj_name)


