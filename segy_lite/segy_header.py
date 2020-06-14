import json
import os
from shapely.geometry import MultiPoint, LineString, mapping
from ibm2ieee import ibm2float32
import numpy as np


class segy(object):
    file_path = os.path.dirname(__file__)
    structure_file = "assets/segyr1_structure.json"
    config_path = os.path.join(file_path, structure_file)
    custom_config = ""  # file_path of the overly config
    pass

    def __init__(self, flo, **kwargs):
        self.__dict__.update(kwargs)
        self.flo = flo  # File Like Object
        self.get_config()
        self.__get_header()
        self.__get_binary_header()
        self.__get_aux_headers()
        self.__set_data_type()

    def get_config(self):
        self.config = json.load(open(self.config_path, "r"))
        if self.custom_config != "":
            custom = json.load(open(self.custom_config, "r"))
            self.config = self.__update(self.config, custom)
        self.byte_order = self.config['byte_order']
        self.byte_order_symbol = ">" if self.byte_order == 'big' else ">"

    def __update(self, d, u):
        for k, v in u.items():
            if isinstance(v, dict):
                d[k] = self.__update(d.get(k, {}), v)
            else:
                d[k] = v
        return d

    def __get_header(self, headers=0):
        if headers == 0:
            # normal headers from rev 0
            self.header = []
            bytes_to_read = 3200
        else:
            # extened headers optional rev1
            self.flo.seek(3600, 0)
            bytes_to_read = 3200 * headers
        bytes = self.flo.read(bytes_to_read)
        textEBCDIC = bytes.decode('cp500')
        textascii = bytes.decode('latin1')
        if textEBCDIC.count(" ") >= textascii.count(' '):
            correctHeader = textEBCDIC
        else:
            correctHeader = textascii
        for i in range(int(bytes_to_read / 80)):  # read each line of 80
            self.header.append(correctHeader[i * 80:(i + 1) * 80].strip())

    def __get_binary_header(self):
        self.flo.seek(0, 0)
        # self.flo.seek(3200,0)
        self.flo.read(3200)
        bin_config = self.config['binary_header']
        bytes = self.flo.read(bin_config['bytes'])
        self.bin_header = {}
        for field, value in bin_config['fields'].items():
            value = self.__get_value(value, bytes)
            self.bin_header[field] = value
        self.trace_samples = (self.bin_header['samples_per_trace'])
        self.trace_sample_interval = int(self.bin_header['sample_interval'] / 1000)
        self.trace_z_range = range(0, int(self.trace_samples * self.trace_sample_interval), self.trace_sample_interval)

    def __get_aux_headers(self):
        self.header_bytes = 3600
        if self.bin_header['extended_header_count'] > 0:
            self.__get_header(self.bin_header['extended_header_count'])
            self.header_bytes += int(self.bin_header['extended_header_count'] * 3200)
        # Todo process the data sections that are documented

    def __set_data_type(self):
        code = self.bin_header['data_sample_format_code']
        if code == 1:
            self.data_bytes = 4
            self.data_format = "ibm"
            self.extract_trace_data = self.__ibm4_decoder
        elif code == 2:
            self.data_bytes = 4
            self.data_format = "int4"
            self.extract_trace_data = self.__int4_decoder
        elif code == 3:
            self.data_bytes = 2
            self.data_format = "int2"
            self.extract_trace_data = self.__int2_decoder
        elif code == 5:
            self.data_bytes = 4
            self.data_format = "ieee",
            self.extract_trace_data = self.__ieee4_decoder
        elif code == 8:
            self.data_bytes = 1
            self.data_format = "int1",
            self.extract_trace_data = self.__int1_decoder
        else:
            self.data_bytes = 4
            self.data_format = "int4",
            self.extract_trace_data = self.__int4_decoder
        self.trace_bytes = self.bin_header['samples_per_trace'] * self.data_bytes
        self.trace_count = (self.flo.seek(0, 2) - self.header_bytes - 1500) / (240 + self.trace_bytes)
        trace = self.get_trace(0)
        scalar_raw = trace[0]['scalar_coordinate']
        if scalar_raw == 0:
            self.scalar = 1
        elif scalar_raw > 0:
            self.scalar = scalar_raw
        else:
            self.scalar = 1 / abs(scalar_raw)

    def get_trace(self, index, sample_mask=[]):
        if index > self.trace_count or index < -self.trace_count:
            return "error", []
        elif (index < 0):
            index = self.trace_count + index + 1
        # trace index starts at zero
        seek_bytes = int((self.trace_bytes + 240) * index)
        self.flo.seek(self.header_bytes + seek_bytes, 0)
        header_raw = self.flo.read(240)
        trace_raw = self.flo.read(self.trace_bytes)
        traceheader = self.__extract_trace_header(header_raw)
        tracedata = self.extract_trace_data(trace_raw)
        if len(sample_mask) != 0:
            tracedata = tracedata[sample_mask]
        return traceheader, tracedata

    def get_traces(self, **kwargs):
        options = {'inline': [-np.inf, np.inf],
                   'crossline': [-np.inf, np.inf],
                   'z_range': [-np.inf, np.inf],
                   'reverse_order': False}
        options.update(kwargs)

        # Create bitmask filters
        filteril = (self.inline >= np.min(options['inline'])) & (self.inline <= np.max(options['inline']))
        filterxl = (self.crossline >= np.min(options['crossline'])) & (self.crossline <= np.max(options['crossline']))
        filterz = ((self.trace_z_range >= np.min(options['z_range'])) & (
                    self.trace_z_range <= np.max(options['z_range'])))
        trace_ids = self.trace_indexes[filteril & filterxl]
        filterskips = np.array(range(len(trace_ids))) % options['skip'] == 0
        trace_ids = trace_ids[filterskips]

        if (options['reverse_order']):
            trace_ids = trace_ids[::-1]

        # Get only data that is needed
        outtraces = []
        outheaders = []
        for id in trace_ids:
            result = self.get_trace(id, filterz)
            outtraces.append(result[1])
            outheaders.append(result[0])

        # Return Results
        z_range = np.array(self.trace_z_range)[filterz]
        z_range = range(np.min(z_range), np.max(z_range), z_range[1] - z_range[0])
        return outheaders, np.array(outtraces), z_range

    def __extract_trace_header(self, header_raw):
        trace_config = self.config['trace_header']
        trace_header = {}
        for field, value in trace_config['fields'].items():
            value = self.__get_value(value, header_raw)
            trace_header[field] = value
        return trace_header

    def scan_trace_headers(self):
        self.flo.seek(self.header_bytes, 0)
        self.trace_indexes = np.array(range(int(self.trace_count + 1)))
        inline = []
        crossline = []
        x_cord = []
        y_cord = []
        for i in self.trace_indexes:
            header_raw = self.flo.read(240)
            self.flo.seek(self.trace_bytes, 1)
            header = self.__extract_trace_header(header_raw)
            inline.append(header['inline'])
            crossline.append(header['crossline'])
            x_cord.append(header['cdp_x'] * self.scalar)
            y_cord.append(header['cdp_y'] * self.scalar)
        self.inline = np.array(inline)
        self.crossline = np.array(crossline)
        self.x_cord = np.array(x_cord)
        self.y_cord = np.array(y_cord)

    def get_3d_parameters(self):
        # create a line / crossline  matrix for calculating geometry
        inline_crossline = np.array([self.inline, self.crossline, np.ones(len(self.inline))]).transpose()
        xypoints = np.array([self.x_cord, self.y_cord, np.ones(len(self.inline))]).transpose()
        # calculate the affine transform matrix
        try:
            z = np.linalg.lstsq(inline_crossline, xypoints, rcond=None)
            transform = z[0]
        except:
            transform = False
        # use the points to make a polygon around the survey and save as well known text
        outline = mapping(MultiPoint(xypoints).convex_hull)
        # compile the return dictonary file
        self.dimensions = 3
        self.transform = transform
        self.geom = outline

        inline_mesh, crossline_mesh = np.meshgrid(range(self.inline.min(), self.inline.max()),
                                                  range(self.crossline.min(), self.crossline.max()))

        self.inline_mesh = inline_mesh.transpose()
        self.crossline_mesh = crossline_mesh.transpose()

    def get_2d_parameters(self):
        # get line trace ranges
        xypoints = np.array([self.x_cord, self.y_cord]).transpose()
        geom = mapping(LineString(xypoints))
        self.dimensions = 2
        self.geom = geom

    def close(self):
        self.flo.close()

    def __int1_decoder(self, raw):
        format = self.byte_order_symbol + "i1"
        data = np.frombuffer(raw, dtype=format)
        return data

    def __int2_decoder(self, raw):
        format = self.byte_order_symbol + "i2"
        data = np.frombuffer(raw, dtype=format)
        return data

    def __int4_decoder(self, raw):
        format = self.byte_order_symbol + "i4"
        data = np.frombuffer(raw, dtype=format)
        return data

    def __ieee4_decoder(self, raw):
        format = self.byte_order_symbol + "f4"
        data = np.frombuffer(raw, dtype=format)
        return data

    def __ibm4_decoder(self, raw):
        format = self.byte_order_symbol + "u4"
        data = np.frombuffer(raw, dtype=format)
        data = ibm2float32(data)
        return data

    def __get_value(self, field, data):
        if "constant" in field:
            return field['constant']
        try:
            pos = field['start_byte'] - 1
            len = field['length_bytes']
            return int.from_bytes(data[pos:pos + len], byteorder='big', signed=True)
        except:
            return 0

    def xy2il(self, xs, ys):
        matrix = np.array([xs, ys, np.ones(len(xs))]).transpose()
        tint = np.linalg.inv(self.transform)
        ic = np.matmul(matrix, tint).astype(int)
        return ic[:, 0:2]

    def ic2xy(self, inlines, crosslines):
        matrix = np.array([inlines, crosslines, np.ones(len(inlines))]).transpose()
        xy = np.matmul(matrix, self.transform)
        return xy[:, 0:2]
