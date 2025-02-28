# Panelize multiple different designs in KiCAD
Requires KiKit and is based on code from [KiKit](https://github.com/yaqwsx/KiKit/tree/master)

KiKit only allows creating panels of the same design. Creating a panel from multiple boards has too many degrees of freedom to implement in a nice GUI.
Hence, for creating such a panel, a scripting attempt is necessary.

This script creates a simple panel of two different designs of identical dimensions placed above each other.
With including configuration it adds a rail on top and bottom and includes tabs with mouse bites in between boards and between board and rail.

**You will have to adjust the script to your own needs**
This Gist is only meant to provide you with a working example.

## Usage
Install KiKit, start KiCAD command prompt, navigate to appropriate directory, run `python panelize_multiple.py`

## License
Derived from KiKit. Same MIT license.

## Versions
Tested with KiCAD 7 and KiKit 1.1.0
