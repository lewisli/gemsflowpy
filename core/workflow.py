import os
from os import listdir
from os.path import isfile, join
import sys
import numpy as np
from enum import Enum
import xml.etree.ElementTree as ET

# Get absolute path of package_directory
package_directory = os.path.dirname(os.path.abspath(__file__)).replace('core','')

# Check if sgems is indeed installed 
sgems_installed = 'sgems' in sys.modules

if sgems_installed is True:
    import sgems

# Global enum for different distribution types
Uniform =1
LogNormal=2
Gaussian=3

class trans_parameter(object):
    def __init__(self,param_type,param_ranges):
        self._type = param_type
        self._ranges = param_ranges
        
    def get_type(self):
        if self._type is Uniform:
            return 'Uniform'
        elif self._type is LogNormal:
            return 'Log Normal'
        elif self._type is Gaussian:
            return 'Gaussian'
            
    def get_param_1_name(self):
        if self._type is Uniform:
            return 'Unif_min_target'
        elif self._type is LogNormal:
            return 'LN_mean_target'
        elif self._type is Gaussian:
            return 'G_mean_target'
            
    def get_param_2_name(self):
        if self._type is Uniform:
            return 'Unif_max_target'
        elif self._type is LogNormal:
            return 'LN_variance_target'
        elif self._type is Gaussian:
            return 'G_variance_target'
    
class geostat_algo(object):
    
    def __init__(self,default_file_path):
        self.default_tree = ET.parse(default_file_path)
        self.current_tree = self.default_tree
        self.current_root = self.current_tree.getroot()
        self.algo_name = self.current_root.find('algorithm').get('name')
        #print 'Read Default Values for Algo:',self.algo_name
        
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

        # for SGSIM/COSGSIM
        output_name = self.get_parameter(['Property_Name'],'value')
        if output_name is not None:
            num_realizations = int(self.get_parameter(['Nb_Realizations'],'value'))
            for i in range(0,num_realizations):
                output_names.append(output_name + '__real' + str(i))
            return output_names

        # for Tetris
        output_name = self.get_parameter(['Property'],'value')
        if output_name is not None:
            num_realizations = int(self.get_parameter(['Nb_Realizations'],'value'))
            for i in range(0,num_realizations):
                output_names.append(output_name + '__real' + str(i))
            return output_names

        # for histogram transforms
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
    
    def __init__(self,output_dir,grid_name,grid_size,num_real):

        # Get all default algorithms
        self.available_algo = dict()
        default_files = [f for f in listdir(package_directory + 'data') \
            if isfile(join(package_directory+'data', f))]
        self.script = ''
        self.output_dir = output_dir
        self.grid_name = grid_name
        self.grid_size = grid_size
        self.num_real = num_real

        # Make sure output directories exist
        if not os.path.exists(output_dir):
            print output_dir,'does not exist'
            os.makedirs(output_dir)

        # Folder where depositional properties are stored
        self.prop_dir = output_dir +'Properties\\' 

        # Folder where facies maps are stored
        self.facies_dir = output_dir + 'Facies\\'

        # make directories
        for path in [self.prop_dir,self.facies_dir]:
            if not os.path.exists(path):
                os.makedirs(path)

        for algos in default_files:
            if 'default.xml' in algos:
                algo_name = algos.replace('_default.xml','')
                self.available_algo[algo_name]=geostat_algo(package_directory+\
                    'data/'+algos)
                
                
    def create_grid(self,name,dim_size,cell_size=[1,1,1],origin=[0,0,0]):
        dim_str = "::".join([str(dim) for dim in dim_size])
        cell_str = "::".join([str(cell) for cell in cell_size])
        origin_str = "::".join([str(val) for val in origin])
        
        outputstr = "::".join([name,dim_str,cell_str,origin_str])
        
        cmd = 'NewCartesianGrid  ' + outputstr + '\n\n'
        
        self.script += cmd
        
        if sgems_installed is True:
            sgems.execute(cmd)

    def save_grid(self,grid_name,obj_name,output_name):

        cmd = 'SaveGeostatGrid  ' + '::'.join([grid_name,self.output_dir+'\\'+
            output_name,'gslib','0',obj_name])

        self.script += cmd + '\n\n'
        
        if sgems_installed is True:
            sgems.execute(cmd)
            
    def save_obj(self,grid_name,obj_names):
        
        for facies, reals in obj_names.iteritems():
            for real in reals:
                output_path = 'Properties\\'+real
                self.save_grid(grid_name,real,output_path)
            
       
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

    def histogram_transf(self,input_names,trans_param):
        # Part 2: Transform clay to Gaussian
        self.available_algo['trans'].reset()
        self.available_algo['trans'].update_parameter(['grid'],\
            'value',self.grid_name)
        self.available_algo['trans'].update_parameter(['props'],\
            'count',str(self.num_real))
        self.available_algo['trans'].update_parameter(\
            ['Use_break_tie_index'],'value','0')
        self.available_algo['trans'].update_parameter(\
            ['ref_type_target'],'value',trans_param.get_type())
        self.available_algo['trans'].update_parameter(\
            [trans_param.get_param_1_name()],'value',\
             str(trans_param._ranges[0]))
        self.available_algo['trans'].update_parameter(\
            [trans_param.get_param_2_name()],'value',\
             str(trans_param._ranges[1]))
        self.available_algo['trans'].update_parameter(\
            ['props'],'value',';'.join(input_names))
        
        output_names = self.run_geostat_algo(\
                'trans')
        
        # Names of realizations after transformation
        if type(output_names) is str:
            output_names = [output_names]

        return output_names
        
    def delete_grid(self,name):
        pass
                
                
    def execute(self):
        pass

class python_workflow(object):
    def __init__(self,output_dir,grid_name,grid_size):
        self.output_dir = output_dir
        self.grid_name = grid_name
        self.grid_size = grid_size


    def read_sgems_files(self,file_name):
        num_header_lines = 3
        raw_input = np.genfromtxt(file_name,skip_header=num_header_lines)
        return raw_input
    

    






  



        

        