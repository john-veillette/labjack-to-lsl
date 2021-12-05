# A LabJack plugin for LabStreamingLayer

`util.labjack.LabJackStream` is a class that handles streaming data from a [Labjack U-series](https://labjack.com/support/datasheets/u6) device to [LabStreamingLayer](https://labstreaminglayer.readthedocs.io/info/intro.html). As is, it works with only the U6 since that device name is hardcoded into the import statements in `util/labjack/stream.py`, but that can be changed super easily.

You can just drop the `util.labjack` module into your project and import `LabJackStream` to use. You'll need some dependencies installed, namely `pylsl`, `liblsl`, `numpy`, `LabJackPython`, and the appropriate driver for your LabJack device. An example environment is in `labjack`

Then, you can start a stream as follows:

```
from util.labjack import LabJackStream
ljs = LabJackStream(n_channels = 4, sfreq = 10000)
ljs.stream_data()
```
which can then be stopped by interrupting the Python process. Whatever number of channels you choose for `n_channels` will always pick the first _n_ channels, which should start with the analog input channels.

Of course, you probably will want to do something else with your Python process in the meantime, in which case you should call `stream_data` in another thread.

```
import threading
ljs = LabJackStream(n_channels = 4, sfreq = 10000)
ljs_thread = threading.Thread(target = ljs.stream_data)
ljs_thread.start()

# other code goes here...

# clean up when you're done
ljs.stop_stream()
ljs_thread.join()
```
In testing, I couldn't go up to the maximal sampling rate from the LabJack U6's [documentation](https://labjack.com/support/datasheets/u6/operation/stream-mode) without dropping samples. But I got almost there e.g. 10 kHz for four analog input channels instead of the advertised 12 kHz.

In old versions of `pylsl`, an error would be thrown when trying to call `pylsl` commands from a thread (other than the main thread) on Linux. Evidently, this has since been fixed -- so if you have this problem, you may just have to update your `pylsl` version.
