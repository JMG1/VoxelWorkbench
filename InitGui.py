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

__title__="Voxel Workbench For FreeCAD"
__author__ = "Javier Martínez García"
__url__ = "http://linuxforanengineer.blogspot.com"

import FreeCAD
import FreeCADGui

class VoxelWorkbench(Workbench):
    import EasyVoxel# this is needed to load the workbench icon
    # __dir__ = os.path.dirname( __file__ ) # __file__ is not working
    Icon = EasyVoxel.__dir__ + '/icons/WorkbenchIcon.svg'
    MenuText = 'Voxel Workbench'
    ToolTip = 'Create models with cubes'

    def GetClassName(self):
        return 'Gui::PythonWorkbench'

    def Initialize(self):
      pass

    def Activated(self):
      import EasyVoxel
      EasyVoxel.startVoxel()
      import VoxelNav
      self.vnav = VoxelNav.VoxelNav()
      FreeCAD.ActiveDocument.recompute()
      self.appendToolbar("VoxelTools",  [ 'ToggleXYMidplane','VoxelToObject' ] )
      self.appendMenu( "VoxelWorkbench", [ 'ToggleXYMidplane', 'VoxelToObject' ] )
      FreeCAD.Console.PrintMessage('Voxel Workbench Loaded\n')


    def Deactivated(self):
      self.vnav.removeNav()

FreeCADGui.addWorkbench(VoxelWorkbench)
