from util.labjack import LabJackStream
import threading
from time import sleep

# start streaming data from labjack on a seperate thread
ljs = LabJackStream(n_channels = 4, sfreq = 10000)
ljs_thread = threading.Thread(target = ljs.stream_data)
ljs_thread.start()

try:
    #print('Started stream with source ID %s.'%ljs.source_id)
    print('Stream started...')
    input("Press Enter to stop.\n")
    ljs.stop_stream()
except Exception:
    ljs.stop_stream()
    print('Labjack stream either ended or failed to start!')

sleep(.5) # wait for stream to close itself

# wait for stream thread to stop
ljs_thread.join()
