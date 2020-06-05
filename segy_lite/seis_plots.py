import matplotlib.pyplot as plt
import matplotlib.colors as colors
import numpy as np
import io
import base64

def plotSeismic(segy_file,**kwargs):
    options = {
            'inline' : [-np.inf,np.inf],
            'crossline' : [-np.inf,np.inf],
            'z_range': [-np.inf,np.inf],
            'tmpdir': 'tmp/',
            'dpi':160,
            'reverse_order': False,
            "color_map": "seismic",
            "variable_density": True,
            "base64out" : False,
            "fileout": False,
            "filelikeobjectout":True}

    options.update(kwargs)
    # key words include
    # in_line = [int, int]
    # x_line = [int, int]
    # z_range = [int, int] time(ms) or depth(units)
    # reverse_order = True/False
    # variable_density = True/False
    # color_map = matplotLlib color map text https://matplotlib.org/gallery/color/colormap_reference.html

    segy_file.scan_trace_headers()
    headers, traces, z_range = segy_file.get_traces(**options)

    fig = plotSeismicLine(traces,**options)
    section_file = io.BytesIO()
    plt.savefig(section_file, format='png', dpi=options['dpi'], antialiased=1)
    plt.close()

    fig = plotFrequencies(traces, segy_file.bin_header['sample_interval'],5)
    freq_file = io.BytesIO()
    plt.savefig(freq_file, format='png', dpi=options['dpi'], antialiased=1)
    plt.close()

    result = {}
    if options['filelikeobjectout']:
        result['section_flo'] = section_file
        result['freq_flo'] = freq_file
    if options['fileout']:
        section_file.seek(0)
        open(options['tmpdir'] + "section.png",'wb').write(section_file.read())
        result['section_file'] = options['tmpdir'] + "section.png"
        freq_file.seek(0)
        open(options['tmpdir'] + "frequency.png", 'wb').write(freq_file.read())
        result['freq_file'] = options['tmpdir'] + "frequency.png"
    if options['base64out']:
        section_file.seek(0)
        freq_file.seek(0)
        result['section_64'] = base64.b64encode(section_file.read()).decode()
        result['freq_64'] = base64.b64encode(freq_file.read()).decode()

    return result

def plotSeismicLine(values_matrix, **kwargs):
    options ={'x_range':range(values_matrix.shape[0]),
             'y_range':range(values_matrix.shape[1]),
             'color_map':"seismic"}
    options.update(kwargs)
    y, x = np.mgrid[options['y_range'],options['x_range']]
    z = np.transpose(values_matrix)
    zmax = np.percentile(z, 98)
    zmin = np.percentile(z, 2)
    if zmin == zmax:
        zmin = -1
        zmax = 1
    norm = colors.Normalize(vmin=zmin, vmax=zmax)
    # fig, (ax0, ax1) = plt.subplots(nrows=2)
    fig = plt.figure(figsize=[16, 9])
    ax0 = fig.add_axes([0, 0, 1, 1])
    ax0.imshow(z, origin='upper', norm=norm, cmap=options['color_map'],interpolation='bicubic',aspect="auto")

    return fig

def plotFrequencies(z_matrix, sample_interval,windows =1):
    zlen = z_matrix.shape[1]
    window_len = zlen/windows
    ubound = 1000 / sample_interval / 2  # nyquest assuming no interpolation

    fig = plt.figure(figsize=[12, 9])
    ax0 = fig.add_axes([.1, .1, .8, .8])
    freq =[]
    amps_raw = []
    amps_db = []
    for i in range(windows):
        z_subset = z_matrix[:,int(i*window_len):int((i+1)*window_len)]
        window_freq, window_amps_raw, window_amps_db = getfrequencies(z_subset, sample_interval)
        freq.append(window_freq)
        amps_raw.append(window_amps_raw),
        amps_db.append(window_amps_db)
        label = ("Window " + str(i+1))
        ax0.plot(freq[i], amps_db[i], label=("Window " + str(i+1)))

    ax0.set_xlim(0,ubound)
    ax0.set_ylim(-50,0)
    ax0.legend()
    plt.xlabel('Hz or Cycles/1000 Survey Units')
    plt.ylabel('DB Down')

    return fig

def getfrequencies(z_matrix, sample_rate):
    # assumes that the first cordinate is a spatial cordiantate and the second is time.
    # run the process on all time cordinates then stackes them to get good average numbers.
    raw = np.fft.fft(z_matrix, axis=1)
    amps_raw = np.abs(raw)
    av_amps = amps_raw.mean(axis=0)
    max_amp = np.max(av_amps)
    freq = np.fft.fftfreq(len(av_amps), sample_rate / 1000)
    amps_DB_down = 20 * np.log10(av_amps / max_amp)
    filter = (freq >= 0)
    freq = freq[filter]
    av_amps = av_amps[filter]
    amps_DB_down = amps_DB_down[filter]
    return freq, av_amps, amps_DB_down

def interpolate(z_matrix,current_sample_rate, requested_sample_rate):
    # This resamples the data along the second dimension of the matrix
    # Check if necessary
    if current_sample_rate == requested_sample_rate:
        return z_matrix
    # If needed inport library and run resample
    import scipy.signal as sig
    new_samples = int(z_matrix.shape[1] * current_sample_rate / requested_sample_rate)
    out_matrix  = sig.resample(z_matrix,new_samples,axis=1)
    return out_matrix



def plot_wiggle(z_matrix,**kwargs):
    options={'color':'black',
             'skip': 10
             }
    options.update(kwargs)

    def wiggle(Data, SH={}, maxval=-1, skipt=1, lwidth=.5, x=[], t=[], gain=1, type='VA', color='black', ntmax=1e+9):
        """
        wiggle(Data,SH)
        """
        import matplotlib.pylab as plt
        import numpy as np
        import copy

        yl = 'Sample number'

        ns = Data.shape[0]
        ntraces = Data.shape[1]

        if ntmax < ntraces:
            skipt = int(np.floor(ntraces / ntmax))
            if skipt < 1:
                skipt = 1

        if len(x) == 0:
            x = range(0, ntraces)

        if len(t) == 0:
            t = range(0, ns)
        else:
            yl = 'Time  [s]'

        # overrule time form SegyHeader
        if 'time' in SH:
            t = SH['time']
            yl = 'Time  [s]'

        dx = x[1] - x[0]
        if (maxval <= 0):
            Dmax = np.nanmax(Data)
            maxval = -1 * maxval * Dmax
            print('segypy.wiggle: maxval = %g' % maxval)

        # fig, (ax1) = plt.subplots(1, 1)'
        fig = plt.gcf()
        ax1 = plt.gca()

        for i in range(0, ntraces, skipt):
            # use copy to avoid truncating the data
            trace = copy.copy(Data[:, i])
            trace[0] = 0
            trace[-1] = 0
            ax1.plot(x[i] + gain * skipt * dx * trace / maxval, t, color=color, linewidth=lwidth)

            if type == 'VA':
                for a in range(len(trace)):
                    if (trace[a] < 0):
                        trace[a] = 0;
                        # pylab.fill(i+Data[:,i]/maxval,t,color='k',facecolor='g')
                # ax1.fill(x[i] + dx * Data[:, i] / maxval, t, 'k', linewidth=0, color=color)
                ax1.fill(x[i] + gain * skipt * dx * trace / (maxval), t, 'k', linewidth=0, color=color)

        ax1.grid(True)
        ax1.invert_yaxis()
        plt.ylim([np.max(t), np.min(t)])

        plt.xlabel('Trace number')
        plt.ylabel(yl)
        if 'filename' in SH:
            plt.title(SH['filename'])
        # ax1.set_xlim(-1, ntraces)
        # plt.show()