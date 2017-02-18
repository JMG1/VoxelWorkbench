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

import FreeCAD
import FreeCADGui
from pivy import coin
import Part
from FreeCAD import Gui

class cameraUpdate:
    def __init__(self, view):
        self.view = view
        # retrieve camera
        self.cam = FreeCADGui.ActiveDocument.ActiveView.getCameraNode()

    def keyboardPosition( self, info ):
        key = info["Key"]
        down = (info["State"] == "DOWN")
        # key logic
        if key == 'r' and (down):
          if FreeCAD.ActiveDocument.BaseCube.behavior == "AddCubes":
             FreeCAD.ActiveDocument.BaseCube.behavior = "RemoveCubes"

          else:
              FreeCAD.ActiveDocument.BaseCube.behavior = "AddCubes"


    def mouseClick( self, info ):
      down = (info["State"] == "DOWN")
      btn = (info["Button"] == "BUTTON1" )
      if down and (btn):
        # retrieve mouse position and underlying objects
        view=Gui.ActiveDocument.ActiveView
        clicked_obj = view.getObjectInfo(view.getCursorPos())
        if clicked_obj is not None:
          # retrieve base object
          bcube = FreeCAD.ActiveDocument.BaseCube
          face_number = clicked_obj['Component']
          if face_number[:4] == "Face":
            face_number = int( face_number[4:] ) -1
            sel_face = bcube.Shape.Faces[face_number]

          if bcube.behavior == "AddCubes":
            cube_pos = sel_face.CenterOfMass + sel_face.normalAt(0,0)*0.5 - FreeCAD.Vector(0.5,0.5,0.5)
            bcube.Proxy.addBlock( cube_pos, "c" )
            if bcube.XY_MidPlane:
              cube_pos = FreeCAD.Vector( cube_pos[0], cube_pos[1], -cube_pos[2] )
              bcube.Proxy.addBlock( cube_pos, "c" )

          else:
            cube_pos = sel_face.CenterOfMass - sel_face.normalAt(0,0)*0.5 - FreeCAD.Vector(0.5,0.5,0.5)
            bcube.Proxy.removeBlock( cube_pos )
            if bcube.XY_MidPlane:
              cube_pos = FreeCAD.Vector( cube_pos[0], cube_pos[1], -cube_pos[2] )
              bcube.Proxy.removeBlock( cube_pos )

          # rebuild geometry
          bcube.Proxy.rebuildGeometry()



class VoxelNav:
  def __init__( self ):
    self.view = Gui.activeDocument().activeView()
    self.cameraUpdate = cameraUpdate(self.view)
    self.keyEvent = self.view.addEventCallback("SoKeyboardEvent", self.cameraUpdate.keyboardPosition)
    self.mouseEvent = self.view.addEventCallback("SoMouseButtonEvent", self.cameraUpdate.mouseClick )

  def removeNav( self ):
    self.view.removeEventCallback( "SoKeyboardEvent", self.keyEvent )
    self.view.removeEventCallback( "SoMouseButtonEvent", self.mouseEvent )

