import numpy as np
import sys

from u6 import U6
import pylsl

class LabJackStream(object):
    '''
    Streams data from a LabJack device (whatever is imported above)
    to labstreaminglayer.

    By default, tries to initialize a U6, but you can put in
    the proper class for your device with device_handle argument.
    '''

    def __init__(self, n_channels = 4, sfreq = 12000,
                        resolution = 1, device_class = U6):
        self.n_channels = n_channels
        self.sfreq = sfreq
        self._res = resolution
        self._init_labjack(device_class)
        self.missed = 0 # keeps track of packet overruns
        self.errors = 0 # keeps track of errors
        self.finished = False
        self.outlet = None
        self._init_lsl() # creates LSL outlet info


    def _init_labjack(self, device_class):
        d = device_class()
        d.getCalibrationData()
        d.streamConfig(
            NumChannels = self.n_channels,
            ChannelNumbers = range(self.n_channels),
            ChannelOptions = [0 for i in range(self.n_channels)],
            ScanFrequency = self.sfreq,
            ResolutionIndex = self._res
        )
        self.device = d

    def _init_lsl(self):
        info = pylsl.StreamInfo(
            'labjack',
            'ADC', # analog-to-digital converter
            self.n_channels,
            self.sfreq,
            'float32',
            source_id = 'labjackUD-%s'%(
                str(self.device.serialNumber)[-4:] # unique identifier
            )
        )
        info.desc().append_child_value("manufacturer", "LabJack")
        info.desc().append_child_value("ResolutionIndex", str(self._res))
        self.info = info

    def _push_to_lsl(self, packet_data):
        r = self.device.processStreamData(packet_data['result'])
        # reformat data to (n_sample) list of samples, each an (n_channel) list
        data = np.array([r['AIN%d'%i] for i in range(self.n_channels)])
        chunk = [data[:, i].tolist() for i in range(data.shape[1])]
        # send to labstreaminglayer
        self.outlet.push_chunk(chunk)

    @property
    def stream_name(self):
        if self.info is not None:
            name = self.info.name()
        else:
            name = None
        return name

    @property
    def source_id(self):
        if self.info is not None:
            sid = self.info.source_id()
        else:
            sid = None
        return sid

    def close_labjack(self):
        try: # since this may have already happened
            self.device.streamStop()
        except:
            pass
        try:
            self.device.close()
        except:
            pass

    def stream_data(self):
        '''
        Starts streaming and continues until stop_stream() method is called.
        '''
        print('Starting stream.')
        self.finished = False
        self.outlet = pylsl.StreamOutlet(self.info)

        try:
            try:
                self.device.streamStart()
            except: # if stream has already been started, restart
                self.device.streamStop()
                self.device.streamStart()
            while not self.finished:
                packet_data = next(self.device.streamData(convert = False))
                if packet_data is None:
                    continue
                self._push_to_lsl(packet_data)
                self.missed += packet_data["missed"]
                self.errors += packet_data["errors"]

            print("Stream stopped...")
            print('%d packets dropped.'%self.missed)
            print('%d errors recorded by labjack.'%self.errors)
            self.close_labjack()
            self.outlet = None

        except:
            self.close_labjack()
            self.outlet = None
            self.finished = True
            e = sys.exc_info()[1]
            print("stream_data exception: %s %s" % (type(e), e))

    def stop_stream(self):
        '''
        Ends stream, which closes labjack and LSL handles.
        '''
        self.finished = True

    def __del__(self):
        self.close_labjack()
