import sys

from gemsflowpy.core import workflow

class porosity_perm_workflow(workflow.sgems_workflow):
    def __init__(self):
        super(porosity_perm_workflow, self).__init__()
        
    
    def execute(self,grid_name,grid_size,porosity_ranges,perm_means):
        
        # Grid Parameters
        num_realizations = len(porosity_ranges)
        
        # Step 1: Create an empty grid of size(100,100,25)
        self.create_grid(grid_name,grid_size)        
        
        for f,(poro_range,perm_mean) in enumerate(zip(porosity_ranges,\
            perm_means)):
                facies_name = 'facies_' + str(f+1)
                
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
                self.available_algo['trans'].update_parameter(['grid'],\
                    'value',grid_name)
                self.available_algo['trans'].update_parameter(\
                    ['Use_break_tie_index'],'value','0')
                self.available_algo['trans'].update_parameter(\
                    ['props'],'value',';'.join(porosity_raw_names))
                    
                self.available_algo['trans'].update_parameter(\
                    ['Unif_min_target'],'value',str(poro_range[0]))
                self.available_algo['trans'].update_parameter(\
                    ['Unif_max_target'],'value',str(poro_range[1]))
                    
                    
                porosity_trans_names = self.run_geostat_algo(\
                        'trans')
                
                # Part 4: Transform permabilities to log-normal
                perm_trans_names = []
                self.available_algo['trans'].reset()
                self.available_algo['trans'].update_parameter(['grid'],\
                    'value',grid_name)
                self.available_algo['trans'].update_parameter(\
                    ['Use_break_tie_index'],'value','0')
                self.available_algo['trans'].update_parameter(\
                    ['ref_type_target'],'value','Log Normal')
                self.available_algo['trans'].update_parameter(\
                    ['LN_mean_target'],'value',str(perm_mean))
                self.available_algo['trans'].update_parameter(\
                    ['LN_variance_target'],'value','1')
                self.available_algo['trans'].update_parameter(\
                    ['props'],'value',';'.join(permeability_raw_names))
                
                perm_trans_names = self.run_geostat_algo(\
                        'trans')