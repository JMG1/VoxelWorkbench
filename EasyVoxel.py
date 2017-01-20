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


__dir__ = os.path.dirname( __file__ )


def stringV3ToList( vector3str ):
    """returns a list from the string, created because JSON is
    feels bad about (...)"""
    v = vector3str.split(",")
    x = float( v[0][1:] )
    y = float( v[1] )
    z = float( v[2][:-1] )
    return ( x, y, z )


class Chunk:
    def __init__( self, obj ):
        #obj.addProperty( "App::PropertyFloatList", "Coordinates" )
        obj.addProperty( "App::PropertyPythonObject", "Coordinates" ).Coordinates = (0,0,0)
        obj.Proxy = self

    def execute( self, fp ):
        pass

    def rebuild( self, chunk_obj ):
        geometry_descriptor = FreeCAD.ActiveDocument.VoxelFolder.GeometryDescriptor
        chunk_geometry = geometry_descriptor[str(chunk_obj.Coordinates)]
        geometry = []
        for voxel_pos, voxel_data in chunk_geometry.iteritems():
            if voxel_data[0] == "c":
                voxel_pos = stringV3ToList( voxel_pos )
                voxel_position = FreeCAD.Vector( voxel_pos[0], voxel_pos[1], voxel_pos[2] )
                geometry.append( Part.makeBox( 1, 1, 1, voxel_position ) )

        chunk_obj.Shape = Part.makeCompound( geometry )


class ViewProviderChunk:
    def __init__(self, obj):
        obj.Proxy = self

    def getDefaultDisplayMode(self):
        return "Flat Lines"

    def getIcon(self):
        __dir__ = os.path.dirname(__file__)
        return __dir__ + '/icons/WorkbenchIcon.svg'

    def paintVoxels( self ):
        pass



class VoxelFolder:
    def __init__( self, obj ):
        obj.addProperty( "App::PropertyPythonObject", "GeometryDescriptor" ).GeometryDescriptor = {}
        obj.addProperty( "App::PropertyString", "behavior" ).behavior = "AddCubes"
        obj.addProperty( "App::PropertyBool", "rebuild" ).rebuild = False
        obj.addProperty( "App::PropertyBool", "clear").clear = False
        obj.addProperty( "App::PropertyBool", "XY_MidPlane").XY_MidPlane = False
        obj.addProperty( "App::PropertyInteger", "NumberOfCubes").NumberOfCubes = 0
        obj.addProperty( "App::PropertyInteger", "NumberOfChunks").NumberOfChunks = 0
        obj.Proxy = self


    def execute( self, fp ):
        if fp.rebuild:
            if fp.clear:
                self.clear()
                fp.clear = False

            self.rebuildGeometry()
            fp.rebuild = False


    def chunkPosFromCubePos( self, cube_pos ):
        """ returns chunk coordinates from cube position:"""
        chunk_coordinates = ( round(cube_pos[0]/16.0), round(cube_pos[1]/16.0), round(cube_pos[2]/16.0) )
        return chunk_coordinates


    def getChunk( self, chunk_coordinates ):
        voxel_folder = FreeCAD.ActiveDocument.VoxelFolder
        va = FreeCAD.Vector( chunk_coordinates[0], chunk_coordinates[1], chunk_coordinates[2] )
        for chunk in voxel_folder.Group:
            vb = FreeCAD.Vector( chunk.Coordinates[0], chunk.Coordinates[1], chunk.Coordinates[2] )
            if ( va - vb ).Length < 0.001:
                return chunk


    def addChunk( self, chunk_coordinates ):
        """ creates a new chunk object from coordinates"""
        voxel_folder = FreeCAD.ActiveDocument.VoxelFolder
        # create chunk object in FreeCAD document
        chunk_obj = FreeCAD.ActiveDocument.addObject( "Part::FeaturePython", "chunk_" + str(chunk_coordinates) )
        voxel_folder.addObject( chunk_obj )
        chunk = Chunk( chunk_obj )
        chunk_view_provider = ViewProviderChunk( chunk_obj.ViewObject )
        chunk_obj.Coordinates = chunk_coordinates
        # log this chunk into the main dictionary containing all chunks (GeometryDescriptor)
        voxel_folder.GeometryDescriptor[str(chunk_coordinates)] = {}
        voxel_folder.NumberOfChunks += 1
        FreeCAD.ActiveDocument.recompute()
        return chunk_obj


    def removeChunk( self, chunk_coordinates ):
        """Transforms the chunk at the given coordinates into entropy and heat.
        Thermodynamics ensure that you'll never see him again..."""
        voxel_folder = FreeCAD.ActiveDocument.VoxelFolder
        chunk = self.getChunk( chunk_coordinates )
        FreeCAD.ActiveDocument.removeObject( chunk.Name )
        del voxel_folder.GeometryDescriptor[str(chunk_coordinates)]
        voxel_folder.NumberOfChunks -= 1
        FreeCAD.ActiveDocument.recompute()


    def rebuildGeometry( self, chunk_coordinates = "All" ):
        """ chunk = All or (x,y,z) (coordinets inside chunk)"""
        voxel_folder = FreeCAD.ActiveDocument.VoxelFolder
        if chunk_coordinates != "All":
            # find chunk
            chunk = self.getChunk( chunk_coordinates )
            chunk.rebuild(chunk)
            #chunk.ViewProvider.paintVoxels()
            FreeCAD.ActiveDocument.recompute()

        else:
            for chunk in voxel_folder.Group:
                chunk.Proxy.rebuild(chunk)
                #chunk.ViewProvider.Proxy.paintVoxels()


    def addBlock( self, cube_pos, block_type, color = (0.85,0.6,0.1) ):
        voxel_folder = FreeCAD.ActiveDocument.VoxelFolder
        chunk_pos = self.chunkPosFromCubePos( cube_pos )
        if str(chunk_pos) in voxel_folder.GeometryDescriptor:
            if str(cube_pos) not in voxel_folder.GeometryDescriptor[str(chunk_pos)]:
                voxel_folder.GeometryDescriptor[str(chunk_pos)][str(cube_pos)] = [block_type, str(color)]
                chunk = self.getChunk( chunk_pos )
                chunk.Proxy.rebuild(chunk)
                #chunk.ViewObject.Proxy.paintVoxels()

        else:
            # create new chunk
            FreeCAD.Console.PrintMessage( "New chunk added\n\n")
            chunk_coordinates = self.chunkPosFromCubePos( cube_pos )
            chunk = self.addChunk( chunk_coordinates )
            voxel_folder.GeometryDescriptor[str(chunk_pos)][str(cube_pos)] = [block_type, str(color)]
            chunk.Proxy.rebuild(chunk)
            #chunk.ViewObject.Proxy.paintVoxels()

        voxel_folder.NumberOfCubes += 1


    def removeBlock( self, cube_pos ):
        voxel_folder = FreeCAD.ActiveDocument.VoxelFolder
        chunk_coordinates = self.chunkPosFromCubePos( cube_pos )
        chunk = self.getChunk( chunk_coordinates )
        if len( voxel_folder.GeometryDescriptor ) > 1:
            del voxel_folder.GeometryDescriptor[str(chunk_coordinates)][str(cube_pos)]
            chunk.Proxy.rebuild(chunk)
            #chunk.ViewProvider.paintVoxels()

        elif len( voxel_folder.GeometryDescriptor ) == 1:
            if len( voxel_folder.GeometryDescriptor[str(chunk_coordinates)] ) == 1:
                FreeCAD.Console.PrintMessage( "Do not try to extinguish us!! (the voxel-people)\n\n")

            else:
                del voxel_folder.GeometryDescriptor[str(chunk_coordinates)][str(cube_pos)]
                chunk.Proxy.rebuild(chunk)

        else:
            self.removeChunk( chunk_coordinates )

        voxel_folder.NumberOfChunks -= 1


    def clear( self ):
        pass


class ViewProviderVx:
    def __init__(self, obj):
        obj.Proxy = self

    def getDefaultDisplayMode(self):
        return "Flat Lines"

    def getIcon(self):
        __dir__ = os.path.dirname(__file__)
        return __dir__ + '/icons/WorkbenchIcon.svg'


def addStartVoxel():
    voxel_folder_obj = FreeCAD.ActiveDocument.addObject( "App::DocumentObjectGroupPython", "VoxelFolder" )
    voxel_folder = VoxelFolder( voxel_folder_obj )
    ViewProviderVx( voxel_folder_obj.ViewObject )
    FreeCAD.ActiveDocument.recompute()
    voxel_folder.addBlock((0,0,0), "c")
    #voxel_folder_obj.rebuild = True
    FreeCAD.ActiveDocument.recompute()


def startVoxel():
    if FreeCAD.ActiveDocument:
        try:
            FreeCAD.ActiveDocument.voxel_folder

        except:
            addStartVoxel()

    else:
        FreeCAD.newDocument("Voxelizer")
        FreeCAD.setActiveDocument("Voxelizer")
        FreeCAD.ActiveDocument= FreeCAD.getDocument("Voxelizer")
        FreeCAD.Gui.ActiveDocument=FreeCAD.Gui.getDocument("Voxelizer")
        addStartVoxel()
