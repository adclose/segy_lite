# Get Header to return
import examples.myconfig
import glob
import json
from segy_lite import *

tempdir = 'tmp/'
#dir = 'testdata/'
dir = 'localtestdata/'

dpi = 160
structure_file = "custom-segy-config.json"

config_path = os.path.join(dir, structure_file)
file_names = glob.glob(dir + '*.s*gy')

for file_name in file_names:
    base_name = os.path.splitext(os.path.basename(file_name))[0]
    file_handle = open(file_name, 'rb')
    if os.path.exists(dir + base_name + "-config.json"):
        config_path = dir + base_name + "-config.json"
        custom_config = json.load(open(config_path,"r"))
        segy_file = segy(file_handle, custom_config=custom_config)
    else:
        segy_file = segy(file_handle)
    segy_file.scan_trace_headers()
    # segy_file.get_3d_parameters()

    bob = segy_file.get_trace(0)

    output = {"header": segy_file.header,
              "config":segy_file.config,
              "inline_range": [int(segy_file.inline.min()), int(segy_file.inline.max())],
              "crossline_range": [int(segy_file.crossline.min()), int(segy_file.crossline.max())],
              "x_range": [int(segy_file.x_cord.min()), int(segy_file.x_cord.max())],
              "y_range": [int(segy_file.y_cord.min()), int(segy_file.y_cord.max())],
              "z_range": [min(segy_file.trace_z_range), max(segy_file.trace_z_range)],
              #"affine_tranform": segy_file.transform
              }

    out_handle = open(tempdir + base_name + '_info.json', 'w')
    json.dump(output, out_handle, indent=4)
    out_handle.close()
