## What is it?
Panel for Nuke that allows you to quickly estimate size of all sources in the script.

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

![esti2](https://cloud.githubusercontent.com/assets/300146/6656068/4151fae2-cb56-11e4-8778-fe37a50f3988.png)

* __Frames to calculate__ — Amount per read node. Default should be just fine for most cases, increase if you want more precision.
* __Show full path__ — Self-descriptive.
* __Estimate disabled nodes__ – Self-descriptive, on by default.

Click 'Run' and enjoy the fact you can use Nuke while script is doing its job in separate thread.
