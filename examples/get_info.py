# Get Header to return
import examples.myconfig
import glob
import json
from segy_lite import *

tempdir = 'tmp/'
dir = 'testdata/'

dpi = 160
structure_file = "custom_segy_config.json"

config_path = os.path.join(dir, structure_file)
file_names = glob.glob(dir +'*.s*gy')

for file_name in file_names:
     base_name = os.path.splitext(os.path.basename(file_name))[0]
     file_handle = open(file_name, 'rb')
     segy_file = segy(file_handle,custom_config= config_path)
     #segy_file.scan_trace_headers()
     #segy_file.get_3d_parameters()

     output = {"header":segy_file.header,
               #"config":segy_file.config,
               #"inline_range" :[int(segy_file.inline.min()), int(segy_file.inline.max())],
               #"crossline_range":[int(segy_file.crossline.min()),int(segy_file.crossline.max())],
               #"z_range":[min(segy_file.trace_z_range),max(segy_file.trace_z_range)],
               #"affine_tranform": segy_file.transform
               }

     out_handle = open(tempdir + base_name + '_info.json','w')
     json.dump(output,out_handle)
     out_handle.close()

