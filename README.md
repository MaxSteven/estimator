## What is it?
Panel for Nuke that allows you to quickly estimate size of all sources in the script.  
Also can be used as imported module to provide same functionality for another tool.

## Installation
1. `cd ~/.nuke && git clone https://github.com/artaman/estimator.git`  
2. Open `~/.nuke/init.py` with your favourite editor  
3. Add the following code:  

```python
#
# Estimator
#
import os, nuke
estimator_path = os.getenv("HOME") + "/.nuke/estimator"
if os.path.exists(estimator_path):
    nuke.pluginAddPath(estimator_path)
    print "~ Adding Estimator panel..."
    import estimator
else:
    print "! Estimator path can't be found, going on..."
```

## Nuke panel
After following steps above you will have a new panel called "Estimator".
By default it is dockable, but can be dragged out and used as a modal window:

![esti3](https://cloud.githubusercontent.com/assets/300146/6656478/287f9e46-cb67-11e4-9e6f-d9a5cf1885b6.png)

* __Frames to calculate__ — Amount per read node. Default should be just fine for most cases, increase if you want more precision.
* __Show full path__ — Self-descriptive.
* __Estimate disabled nodes__ – Self-descriptive, on by default.
* __Sort by size__ – Wait until calculation is done and display results sorted.

Click 'Run' and enjoy the fact you can use Nuke while script is doing its job in separate thread.

## Usage within other script

```python
estimator_path = os.getenv("HOME") + "/.nuke/estimator"
sys.path.append(estimator_path)
from estimator_panel import estimatorPanel

calc = estimatorPanel()
reads = calc.evaluate_script(2)

print reads
# {'/path/to/sequence_%0Xd.xxx': [first_frame, last_frame, size_in_bytes]}
```
