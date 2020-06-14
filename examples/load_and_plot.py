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
# file_names = [datadir + "volve-3d.segy"]

for file_name in file_names:
    base_name = os.path.splitext(os.path.basename(file_name))[0]
    file_handle = open(file_name, 'rb')

    # segy_file = segy(file_handle,custom_config= config_path)
    segy_file = segy(file_handle)
    # segy_file.scan_trace_headers() # Enables 3D extractions
    # segy_file.get_3d_parameters()  # Enables other 3D functions

    # Plot random colorbar
    random_color_map = plt.colormaps()[np.random.randint(len(plt.colormaps()))]
    z_range = [1000,2500]
    result = plotSeismic(segy_file, z_range=z_range, skip=1, reverse_order=False, variable_density=True,
                         color_map=random_color_map)
    local_location = tempdir + base_name + 'plot'+random_color_map+'.png'
    open(local_location, "wb").write(result['section_flo'].read())

    # Plot Seismic color
    result = plotSeismic(segy_file, z_range=z_range, skip=1, reverse_order=False, variable_density=True,
                         color_map='seismic')
    local_location = tempdir + base_name + 'plot_normal.png'
    open(local_location, "wb").write(result['section_flo'].read())

    # Plot wiggle
    result = plotSeismic(segy_file, z_range=z_range, skip=1, reverse_order=False, variable_density=False,
                         color_map='seismic')
    local_location = tempdir + base_name + 'plotwiggle.png'
    open(local_location, "wb").write(result['section_flo'].read())

    # Plot reverse gray
    result = plotSeismic(segy_file, z_range=z_range, skip=1, reverse_order=True, variable_density=True,
                         color_map='gray')
    local_location = tempdir + base_name + 'plot_grey_reverse.png'
    open(local_location, "wb").write(result['section_flo'].read())


    local_freq = tempdir + base_name + 'freq.png'
    open(local_freq, "wb").write(result['freq_flo'].read())
    segy_file.close()
