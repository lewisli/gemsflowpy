import sys
import os
import itertools
import numpy as np
from gemsflowpy.core import workflow

# Workflows that run internally in sgems

class sgsim_workflow(workflow.sgems_workflow):
    def __init__(self,grid_name,grid_size,facies_names,prop_name,trans_params,\
                 num_real,output_dir):
        super(sgsim_workflow, self).__init__(output_dir,grid_name,grid_size,num_real)

        self.facies_names = facies_names
        self.prop_name = prop_name
        self.trans_params = trans_params
        
    def execute(self):
        
        # Step 1: Create a grid
        self.create_grid(self.grid_name,self.grid_size)
        
        # Dictionary to store output realization names
        # key is facies name
        sgsim_output_names = dict()
        sgsim_trans_names = dict()
        
        # Perform SGSIM on each facies using default settings
        for f,(trans_param,facies_name) in enumerate(zip(self.trans_params\
            ,self.facies_names,)):
                self.available_algo['sgsim'].reset()
                self.available_algo['sgsim'].update_parameter(['Grid_Name'],\
                    'value',self.grid_name)
                self.available_algo['sgsim'].update_parameter(['Property_Name'],\
                    'value',facies_name+'_'+self.prop_name)
                
                # Set number of realizations
                self.available_algo['sgsim'].update_parameter(['Nb_Realizations'],\
                    'value',str(self.num_real))

                 # Get clay realization names
                sgsim_real_names = self.run_geostat_algo('sgsim')
                
                # Handles 1 realization case
                if type(sgsim_real_names) is str:
                    sgsim_real_names = [sgsim_real_names]

                # Names of realizations after sgsim
                sgsim_output_names[facies_name] = sgsim_real_names

                # Perform any necessary histogram transformations
                sgsim_trans_names[facies_name] = self.histogram_transf(\
                    sgsim_real_names,trans_param)

                
        # Save objects to disk
        self.save_obj(self.grid_name,sgsim_output_names)
        self.save_obj(self.grid_name,sgsim_trans_names)
                
        return sgsim_output_names,sgsim_trans_names

class cosgsim_workflow(workflow.sgems_workflow):
    def __init__(self,grid_name,grid_size,facies_names,prop_name,trans_params,\
                 num_real,output_dir):
        super(cosgsim_workflow, self).__init__(output_dir,grid_name,\
            grid_size,num_real)

        self.facies_names = facies_names
        self.prop_name = prop_name
        self.trans_params = trans_params
        self.num_real = num_real

    def execute(self,secondary_vars):
        
        # Step 1: Create a grid
        self.create_grid(self.grid_name,self.grid_size)
        
        # Dictionary to store output realization names
        # key is facies name
        cosgsim_output_names = dict()
        cosgsim_trans_names = dict()
        
        
        # Part 2: Generate permability realizations
        # Perform SGSIM on each facies using default settings
        
        # Iterate over facies
        for f,(trans_param,facies) in enumerate(zip(self.trans_params\
            ,self.facies_names)):
             self.available_algo['colocated-sgsim'].reset()
             self.available_algo['colocated-sgsim'].update_parameter(\
                            ['Grid_Name'],'value',self.grid_name)
             
             # Iterate over each of the secondary variables
             secondary_var_names = []
             for secondary_real in secondary_vars[facies]:
                 self.available_algo['colocated-sgsim'].update_parameter(\
                            ['Secondary_property'],'value',secondary_real)
                 
                 # Generate only a single realization for now
                 self.available_algo['colocated-sgsim'].update_parameter(\
                            ['Property_Name'],'value',secondary_real+\
                            '_'+self.prop_name)
                 
                 
                 # Get clay realization names
                 real_name = self.run_geostat_algo('colocated-sgsim')
                
                 # Handles 1 realization case
                 if type(real_name) is str:
                    real_name = [real_name]

                 secondary_var_names.append(real_name)

             cosgsim_output_names[facies]= [str(v[0]) for v in secondary_var_names]

            # Perform any necessary histogram transformations
             cosgsim_trans_names[facies] = self.histogram_transf(\
                cosgsim_output_names[facies],trans_param)

         # Save objects to disk
        self.save_obj(self.grid_name,cosgsim_output_names)
        self.save_obj(self.grid_name,cosgsim_trans_names)
        
        return cosgsim_output_names,cosgsim_trans_names


class tetris_workflow(workflow.sgems_workflow):
    def __init__(self,grid_name,grid_size,num_real,output_dir):
        super(tetris_workflow, self).__init__(output_dir,grid_name,grid_size,\
            num_real)

    def execute(self):

        num_facies_map = self.num_real
        
        # Step 1: Create an empty grid of size(100,100,25)
        self.create_grid(self.grid_name,self.grid_size)

        # Generate training image realizations
        self.available_algo['TetrisTiGen'].reset()
        self.available_algo['TetrisTiGen'].update_parameter(['Grid'],\
            'value',self.grid_name)
        self.available_algo['TetrisTiGen'].update_parameter(['Property'],\
            'value','Facies_map')
        self.available_algo['TetrisTiGen'].update_parameter(['Nb_Realizations']\
            ,'value',str(num_facies_map))

        facies_map_names = self.run_geostat_algo('TetrisTiGen')

        for facies_map in facies_map_names:

            output_obj_path = 'Facies\\' + facies_map + '.sgems'
            self.save_grid(self.grid_name,facies_map,output_obj_path)

        return facies_map_names

