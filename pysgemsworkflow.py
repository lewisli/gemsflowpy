from os import listdir
from os.path import isfile, join
import sys

import xml.etree.ElementTree as ET

sgems_installed = 'sgems' in sys.modules

if sgems_installed is True:
    import sgems
    

class geostat_algo(object):
    
    def __init__(self,default_file_path):
        self.default_tree = ET.parse(default_file_path)
        self.current_tree = self.default_tree
        self.current_root = self.current_tree.getroot()
        self.algo_name = self.current_root.find('algorithm').get('name')
        print 'Read Default Values for Algo:',self.algo_name
        
    def update_parameter(self,p_names,p_type,p_val):
        
        # Check if tree contains p_name
        p_node = self.current_root
        
        # p_names is a list containing all the nodes we need to traverse
        for p_name in p_names:
            p_node_next = p_node.find(p_name)
            
            # if the node is not found, need to add it in
            if p_node_next is None:
                p_node.append(ET.Element(p_name))
                p_node_next = p_node.find(p_name)

            p_node = p_node_next
        
        if p_node is None:
            #print 'Error: Algorithm does not have a parameter named:',p_name
            return False
        else:
            p_node.set(p_type,p_val) 
            
    def get_parameter(self,p_names,p_type):
        
         # Check if tree contains p_name
        p_node = self.current_root
        
        # p_names is a list containing all the nodes we need to traverse
        for p_name in p_names:
            p_node = p_node.find(p_name)
            
            if p_node is None:
                return None
            
        return p_node.get(p_type) 
        
            
    def delete_parameter(self,p_names):
        p_node = self.current_root
        
        # p_names is a list containing all the nodes we need to traverse
        for p_name in p_names:
            p_node = p_node.find(p_name)

    def get_output_names(self):
        output_names = []

        output_name = self.get_parameter(['Property_Name'],'value')
        if output_name is not None:
            num_realizations = int(self.get_parameter(['Nb_Realizations'],'value'))
            for i in range(0,num_realizations):
                output_names.append(output_name + '__real' + str(i))
            return output_names
            
        output_name = self.get_parameter(['props'],'value')
        if output_name is not None:
            output_props = output_name.split(';')
            output_suffix = self.get_parameter(['out_suffix'],'value')
            
            for prop in output_props:
                output_names.append(prop + output_suffix )
        
        
            
        return output_names
            
            
    def execute(self):
        
        # Generate command string
        execute_cmd = 'RunGeostatAlgorithm  ' + self.algo_name + \
            '::/GeostatParamUtils/XML::' + self.to_str()
       
        return self.get_output_names(),execute_cmd
        
            
    def to_str(self):
        self.xmlstr = ET.tostring(self.current_root, method='xml')
        return self.xmlstr
    
    def reset(self):
        self.current_tree = self.default_tree
        self.current_root = self.current_tree.getroot()

class sgems_workflow(object):
    
    def __init__(self):
        # Get all default algorithms
        self.available_algo = dict()
        default_files = [f for f in listdir('data') if isfile(join('data', f))]
        self.script = ''

        for algos in default_files:
            if 'default.xml' in algos:
                algo_name = algos.replace('_default.xml','')
                self.available_algo[algo_name]=geostat_algo('data/'+algos)
                
                
    def create_grid(self,name,dim_size,cell_size=[1,1,1],origin=[0,0,0]):
        dim_str = "::".join([str(dim) for dim in dim_size])
        cell_str = "::".join([str(cell) for cell in cell_size])
        origin_str = "::".join([str(val) for val in origin])
        
        outputstr = "::".join([name,dim_str,cell_str,origin_str])
        
        cmd = 'NewCartesianGrid  ' + outputstr + '\n\n'
        
        self.script += cmd
        
        if sgems_installed is True:
            sgems.execute(cmd)
            
        
    def run_geostat_algo(self,algo_name):
        
        output_names, cmd = self.available_algo[algo_name].execute()
        self.script += cmd + '\n\n'
        
        # If we are running inside a sgems session
        if sgems_installed is True:
            sgems.execute(cmd)
            
        if len(output_names) is 1:
            return output_names[0]
        else:
            return output_names

       
        
    def delete_grid(self,name):
        pass
                
                
    def execute(self):
        pass
        

class porosity_perm_workflow(sgems_workflow):
    def __init__(self):
        super(porosity_perm_workflow, self).__init__()
        
    
    def execute(self):
        
        # Grid Parameters
        grid_name = 'case1'
        grid_size = [100,100,25]
        num_realizations = 3
        
        porosity_ranges = [[0,0.1],[0.1,0.25],[0.2,0.35]]
        perm_means = [0.3,0.5,0.6]
        

        
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

x = porosity_perm_workflow()
x.execute()

text_file = open("scripts/Trial1.txt", "w")
text_file.write("%s" % x.script)
text_file.close()



  



        

        