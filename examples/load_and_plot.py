# Get Header to return
import examples.myconfig
import glob
from segy_lite import *

tempdir = 'tmp/'
datadir = 'testdata/'

dpi = 160
structure_file = "custom-segy-config.json"

config_path = os.path.join(datadir, structure_file)
file_names = glob.glob(datadir + '*.s*gy')
#file_names = [datadir + "volve-3d.segy"]

for file_name in file_names:
    base_name = os.path.splitext(os.path.basename(file_name))[0]
    file_handle = open(file_name, 'rb')

    # segy_file = segy(file_handle,custom_config= config_path)
    segy_file = segy(file_handle)
    #segy_file.scan_trace_headers() # Enables 3D extractions
    #segy_file.get_3d_parameters()  # Enables other 3D functions

    result = plotSeismic(segy_file, z_range=[0, 2500],skip=1,reverse_order=False,variable_density=True,color_map='gray')
    local_location = tempdir + base_name + 'plotgray.png'
    open(local_location, "wb").write(result['section_flo'].read())
    local_freq = tempdir + base_name + 'freq.png'
    open(local_freq, "wb").write(result['freq_flo'].read())
    segy_file.close()
