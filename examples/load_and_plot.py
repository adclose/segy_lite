# Get Header to return
import examples.myconfig
import glob
from segy_lite import *

tempdir = 'tmp/'
dir = 'testdata/'

dpi = 160
structure_file = "custom_segy_config.json"

config_path = os.path.join(dir, structure_file)
file_names = glob.glob(dir +'*.s*gy')
file_names=[dir + "volve_3d.segy"]
for file_name in file_names:
     base_name = os.path.splitext(os.path.basename(file_name))[0]
     file_handle = open(file_name, 'rb')

     #segy_file = segy(file_handle,custom_config= config_path)
     segy_file = segy(file_handle)
     segy_file.scan_trace_headers()
     segy_file.get_3d_parameters()
     result = plotSeismic(segy_file,z_range=[0,2500])

     local_location = tempdir + base_name + 'plot.png'
     open(local_location,"wb").write(result['section_flo'].read())
     local_freq = tempdir + base_name + 'freq.png'
     open(local_freq, "wb").write(result['freq_flo'].read())
     segy_file.close()