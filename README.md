# VoxelWorkbench
Voxel Workbench for FreeCAD

![show](https://2.bp.blogspot.com/-dYmMB_VxA1s/WH35o4WX3QI/AAAAAAAAC7w/nUXfOiqdakI-9Ga5gscOpKtZSuAUL5uawCLcB/s400/Captura%2Bde%2Bpantalla%2Bde%2B2017-01-17%2B10-21-36.png)

[Demo video](https://www.youtube.com/watch?v=nE0LYK__R5U)

[FreeCAD forum thread](https://forum.freecadweb.org/viewtopic.php?f=24&t=20013&hilit=voxel)

### Installation
#####Using git on Ubuntu & Mint:
- Open the terminal with the keys **ctrl+alt+t**

- Install git:  ***sudo apt-get install git***

- Clone repository:  ***git clone https://github.com/JMG1/VoxelWorkbench ~/.FreeCAD/Mod/VoxelWorkbench***

That's all, the next time you launch FreeCAD the workbench should be incorporated automagically.

#####To install manually download this repository as ZIP and:
- For Ubuntu, Mint and similar OS's, extract it inside */home/username/.FreeCAD/Mod*
- For Windows, extract it inside *drive: \Users\your_user_name\AppData\Roaming\FreeCAD\Mod*


### How to use it:

* Place a cube with a click of the left mouse button over the face of an existing cube.
* Press "r" key to alternate between creating and destroying cubes.
* Select "XY_MidPlane" as true in the properties tab of the BaseCube object to place cubes symmetrically to the XY plane.
* Remove all blocks by setting the "clear_cubes" property to true and then "rebuild" to true


### TODO:
* Stop voxel nav when changing workbench
* Some screen freezing when playing with big amounts of cubes
* Converto to a normal FreeCAD object or STL file
* Place other objects (wedges, arcs...)
