# -*- coding: utf-8 -*-
# Voxel Workbench For FreeCAD
# (c) 2017 Javier Martínez García
#***************************************************************************
#*   (c) Javier Martínez García 2017                                      *
#*                                                                         *
#*   This program is free software; you can redistribute it and/or modify  *
#*   it under the terms of the GNU General Public License (GPL)            *
#*   as published by the Free Software Foundation; either version 2 of     *
#*   the License, or (at your option) any later version.                   *
#*   for detail see the LICENCE text file.                                 *
#*                                                                         *
#*   This program is distributed in the hope that it will be useful,       *
#*   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
#*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
#*   GNU Lesser General Public License for more details.                   *
#*                                                                         *
#*   You should have received a copy of the GNU Library General Public     *
#*   License along with FreeCAD; if not, write to the Free Software        *
#*   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
#*   USA                                                                   *
#*                                                                         *
#***************************************************************************/


import os
import FreeCAD
import Part


__dir__ = os.path.dirname(__file__)


class createBaseBlock:
  def __init__( self, obj ):
    obj.addProperty( "App::PropertyPythonObject", "GeometryDescriptor" ).GeometryDescriptor= [("c",0.0,0.0,0.0)]
    obj.addProperty( "App::PropertyString", "behavior" ).behavior = "AddCubes"
    obj.addProperty( "App::PropertyBool", "rebuild" ).rebuild = False
    obj.addProperty( "App::PropertyBool", "clear_cubes").clear_cubes = False
    obj.addProperty( "App::PropertyBool", "XY_MidPlane").XY_MidPlane = False
    obj.addProperty( "App::PropertyInteger", "VoxelNumber" ).VoxelNumber = 1
    obj.Proxy = self

  def execute( self, fp ):
    if fp.rebuild:
      if fp.clear_cubes:
        self.clearCubes()
        fp.clear_cubes = False

      self.rebuildGeometry()
      fp.rebuild = False



  def rebuildGeometry( self ):
    bcube = FreeCAD.ActiveDocument.BaseCube
    geometry = []
    for geom in bcube.GeometryDescriptor:
      if geom[0] == "c":
        geometry.append( Part.makeBox(1,1,1, FreeCAD.Vector( geom[1],geom[2],geom[3] ) ) )

    bcube.Shape = Part.makeCompound( geometry )
    bcube.VoxelNumber = len( bcube.GeometryDescriptor )


  def addBlock( self, cube_pos, block_type ):
    bcube = FreeCAD.ActiveDocument.BaseCube
    for geom in bcube.GeometryDescriptor:
      v = FreeCAD.Vector( geom[1], geom[2], geom[3] )
      if ( v - cube_pos ).Length < 0.01:
        return

    new_block = ( block_type, cube_pos[0],cube_pos[1],cube_pos[2] )
    bcube.GeometryDescriptor.append( new_block )


  def removeBlock( self, cube_pos ):
    fp = FreeCAD.ActiveDocument.BaseCube
    if len(fp.GeometryDescriptor) > 1:
      i = 0
      for geom in fp.GeometryDescriptor:
        v = FreeCAD.Vector( geom[1], geom[2], geom[3] )
        if ( v - cube_pos ).Length < 0.01:
          del fp.GeometryDescriptor[i]
          i -= 1
          break

        i += 1

    else:
      FreeCAD.Console.PrintError("Do not try to estinguish us (the voxel people)!!\n\n")


  def clearCubes( self ):
    fp = FreeCAD.ActiveDocument.BaseCube
    fp.GeometryDescriptor = [("c",0.0,0.0,0.0)]
    self.rebuildGeometry()


class ViewProviderVx:
   def __init__(self, obj):
      ''' Set this object to the proxy object of the actual view provider '''
      obj.Proxy = self

   def getDefaultDisplayMode(self):
      ''' Return the name of the default display mode. It must be defined in getDisplayModes. '''
      return "Flat Lines"

   def getIcon(self):
      __dir__ = os.path.dirname(__file__)
      return __dir__ + '/icons/WorkbenchIcon.svg'



def startVoxel():
  if FreeCAD.ActiveDocument:
    try:
      FreeCAD.ActiveDocument.BaseCube

    except:
      bcube_obj = FreeCAD.ActiveDocument.addObject( "Part::FeaturePython", "BaseCube" )
      bcube = createBaseBlock( bcube_obj )
      ViewProviderVx( bcube_obj.ViewObject )
      bcube_obj.ViewObject.ShapeColor = (0.80,0.39,0.39)
      bcube_obj.rebuild = True
      FreeCAD.ActiveDocument.recompute()

  else:
    FreeCAD.newDocument("Voxelizer")
    FreeCAD.setActiveDocument("Voxelizer")
    FreeCAD.ActiveDocument= FreeCAD.getDocument("Voxelizer")
    FreeCAD.Gui.ActiveDocument=FreeCAD.Gui.getDocument("Voxelizer")
    bcube_obj = FreeCAD.ActiveDocument.addObject( "Part::FeaturePython", "BaseCube" )
    bcube = createBaseBlock( bcube_obj )
    ViewProviderVx( bcube_obj.ViewObject )
    bcube_obj.ViewObject.ShapeColor = (0.80,0.39,0.39)
    bcube_obj.rebuild = True
    FreeCAD.ActiveDocument.recompute()


# tools
class VoxelToObject:
    def GetResources(self):
        return {'Pixmap': __dir__ + '/icons/ToRealPartIcon.svg',
                'MenuText': 'Voxel to FreeCAD Object',
                'ToolTip': 'Creates a FreeCAD geometry object from voxels'}

    def IsActive(self):
      return True

    def Activated(self):
      FreeCAD.Console.PrintMessage( "This can take a while..." )
      FreeCAD.Gui.updateGui()
      bcube = FreeCAD.ActiveDocument.getObject("BaseCube")
      geometry = []
      for geom in bcube.GeometryDescriptor:
        if geom[0] == "c":
          geometry.append( Part.makeBox(1.001,1.001,1.001, FreeCAD.Vector( geom[1],geom[2],geom[3] ) ) )

      obj = FreeCAD.ActiveDocument.addObject("Part::Feature", bcube.Label + "_obj" )
      obj.Shape = geometry[0]
      geom_max, geom_count = len(geometry), 0
      for i in xrange( len( geometry ) - 1 ):
        obj.Shape = obj.Shape.fuse( geometry[i+1] )
        geom_count += 1
        if geom_count % 13 == 0:
          FreeCAD.Console.PrintMessage( str( geom_count ) + " of "+str( geom_max )+ " voxels done\r")
          FreeCAD.Gui.updateGui()

      obj.Shape = obj.Shape.removeSplitter()
      bcube.ViewObject.Visibility = False
      FreeCAD.Console.PrintMessage("\nDone!\n")



class ObjectToVoxel():
  def GetResources(self):
      return {'Pixmap': __dir__ + '/icons/ObjectToVoxelIcon.svg',
              'MenuText': 'FreeCAD object to voxel',
              'ToolTip': 'Creates a voxel model of the selected object\n' +
              'Be careful with model size, it may result in a very\n' +
              ' big amount of cubes'}

  def IsActive(self):
    return True

  def Activated(self):
    FreeCAD.Console.PrintMessage( "This can take a while..." )
    FreeCAD.Gui.updateGui()
    bcube = FreeCAD.ActiveDocument.BaseCube
    selobj = FreeCAD.Gui.Selection.getSelectionEx()[0].Object
    bbox = selobj.Shape.BoundBox
    X = ( round( bbox.XMin ) - 1, round( bbox.XMax ) + 1 )
    Y = ( round( bbox.YMin ) - 1, round( bbox.YMax ) + 1 )
    Z = ( round( bbox.ZMin ) - 1, round( bbox.ZMax ) + 1 )
    cube_number = 0
    for zi in xrange( abs( int( Z[1]-Z[0] ) ) ):
      z = Z[0] + zi
      for yi in xrange( abs( int( Y[1]-Y[0] ) ) ):
        y = Y[0] + yi
        for xi in xrange( abs( int( X[1]-X[0] ) ) ):
          x = X[0] + xi
          probe_v = FreeCAD.Vector( x+0.5, y+0.5, z+0.5 )
          if selobj.Shape.isInside( probe_v, 0.2, True ):
            bcube.GeometryDescriptor.append( ( "c", x, y, z ) )
            cube_number += 1
            if cube_number % 7 == 0:
              FreeCAD.Console.PrintMessage( str(cube_number) + " voxels generated\n" )

    bcube.rebuild = True
    FreeCAD.ActiveDocument.recompute()
    FreeCAD.Console.PrintMessage("Done!\n")


class ToggleXYMidplane:
    def GetResources(self):
        return {'Pixmap': __dir__ + '/icons/midplaneIcon.svg',
                'MenuText': 'Toggle XY Mirroring',
                'ToolTip': 'Mirrors cubes construction/destruction along XY pane'}

    def IsActive(self):
      return True

    def Activated(self):
        try:
          bc = FreeCAD.ActiveDocument.getObject( "BaseCube" )
          bc.XY_MidPlane = not( bc.XY_MidPlane )

        except:
          FreeCAD.Console.PrintError("No base cube object??")



if FreeCAD.GuiUp:
    FreeCAD.Gui.addCommand('ToggleXYMidplane', ToggleXYMidplane())
    FreeCAD.Gui.addCommand('VoxelToObject', VoxelToObject())
    FreeCAD.Gui.addCommand('ObjectToVoxel', ObjectToVoxel())
