#!/usr/bin/env python
#====================================================
# Script: Saving OBJ Mesh
# (Cambios hechos  en GoZ para adaptarlo a exportar de  Modo a Maya)
#====================================================
import lx
import os
import socket 

def checkIfMeshId(projectPath, mesh, name, meshID):
    """Checks if exists another Object having the same name as the mesh
    This function asks the user what to do.
    
    If the object is not a mesh, gets all the children meshes 
    
     Args:
         projectPath: a str with the path where the exported file will be
         mesh: a string that representes one of the mesh in the scene
         name: a str with the name of the mesh
         meshID: the new name if needed
    returns
        name:  as tr with the new value
        abort: is the uses choose to cancel
    """
    abort = False
    
    if os.access(projectPath + meshID + ".obj" , os.W_OK):
       
        msg = "There is already an existing Go file [" + name + "] in the Go project folder.\n"
        msg = msg + "Do you want to replace it?\n'Yes' to replace, 'No' to rename the mesh " + name + ", 'Cancel' to cancel export"
        res = showDialog("Exporting mesh object " + name, msg, "yesNoCancel")
        
        if (res == "ok"):
            # replace existing Object
            lx.out('  -> itemID=({0}): set GoMo tag to "{0}"'.format(mesh, name))
            meshID = name
            lx.eval('select.drop item')
            lx.eval('select.item {0} set'.format(mesh))
            lx.eval('item.tag string GoMo "{0}"' %(meshID))
        if (res == "no"):
            #rename the mesh to an unique Object
            name = meshID
            lx.eval('select.drop item')
            lx.eval('select.item {0} set'.format(mesh))
            lx.eval('item.name "{0}"'.format(meshID))
            lx.eval('item.tag string GoMo "{0}"'.format(meshID))
        if (res == "cancel"):
            abort = True
    
    return name, meshID, abort

def exportMeshes():
    """Exports to obj files all the meshes in the scene
    """
    ##TODO ask the user for the projectPath and where to save the OBJ files
    
    projectPath = "/the/path/of/your/project/"
  
    meshList = getAllMeshes()
   
    # Process each selected item.
    for mesh in meshList:
       
        lx.out('Processing item "{0}"'.format(mesh))

       
        lx.eval('select.drop item')
        lx.eval('select.item {0} set'.format(mesh))
        
        # Gets the meshID of the mesh.
        name = lx.eval('item.name ?')
        meshID = lx.eval('item.tag string GoMo ?')

        lx.out('  item ID[{0}] has name "{1}" and meshID "{2}"'.format(mesh, name, meshID))
        
        name, meshID, abort = checkIfMeshId(projectPath, mesh, name, meshID)

        # If export was not cancelled, then export:
        if not abort:
            lx.out('  exporting the mesh...')
            #Creates Obj file if needed
            if not os.access("{0}/objMeshList.txt".format(projectPath), os.F_OK):
                goListFile = open("{0}/objMeshList.txt".format(projectPath), "w")
                goListFile.close()
            

            lx.out('  exporting the mesh(ID[{0}], name "{1}", meshID  to "{2}")'.format(mesh, name, meshID, projectPath))
            objFileList = open("{0}/objMeshList.txt".format(projectPath), "a")
            line = "{0}\n".format(name)
            objFileList.write(line)
            objFileList.close()
        
            # Create a temporary scene and copy the meshes there.
            lx.eval('select.drop item')
            lx.eval('select.item '.format(mesh))
            lx.eval('select.copy')
            lx.eval('scene.new')
            lx.eval('select.paste')

            # Then saves this temporary scene in a OBJ file.
            path = "{0}/{1}.obj".format(projectPath, name)
            lx.out('Note: Exporting "{0}"'.format(path))
            lx.eval('scene.saveAs "{0}" wf_OBJ true'.format(path))

            #Destroys this temporary scene.
            lx.eval('!scene.close')


    # Closes the Object list file and launch Maya.
    if meshList:
        lx.out('{0} meshes exported to Maya!!!'.format(len(meshList)))
        # executes a mel script to load the objs files
        sourceMel()
    else:
        lx.out('No mesh selected')


def getAllChildrenMeshes(selectedObject, meshList):
    """Fills the meshlist with all the children that are a mesh
    
     Args:
         selectedObject: on object in the scene
         meshList: a list that will contain the meshes of the scene
    """
    def convertToList(cTuple):
        if type(cTuple) == tuple: 
            return  list(childrenTuple)
        else:
            return [childrenTuple]
    
    childrenTuple = lx.eval('query sceneservice item.children ? {0}'.format(selectedObject))
    childrenList = convertToList(childrenTuple)
    
    while childrenList:
        originaLenght = len(childrenList)
        for child in childrenList:   
            childType = lx.eval('query sceneservice item.type ? {0}'.format(child))
            if childType == 'groupLocator':
                childrenTuple = lx.eval('query sceneservice item.children ? {0}'.format(child))
                childrenList.extend(convertToList(childrenTuple))
            elif childType == 'mesh':
                meshList.append(child)
       
        childrenList[originaLenght:]
        
def getAllMeshes():
    """Construct a list just the scene meshes

    returns
        the mesh list
    """
    meshList = []
    lx.out('selecting all the meshes ...')
    allObjects = lx.eval('query sceneservice selection ? all')

    if type(allObjects) == tuple:
        #This means that more than one object is in the scene
        lx.out('allObjects = "{0}"'.format(allObjects))
        for selectedObject in allObjects:
            isAMesh(selectedObject, meshList)
    else:
        if type(allObjects) == str:
            selectedObject = allObjects
            lx.out('allObjects is not "None"')
            lx.out('allObjects = "{0}"'.format(allObjects))
            isAMesh(selectedObject, meshList)
            
        else:
            lx.out('allObjects is "None"')

    return meshList

def isAMesh(selectedObject, meshList):
    """Checks if the selectedObject is a mesh
    
    If the object is not a mesh, gets all the children meshes 
    
     Args:
         selectedObject: on object in the scene
         meshList: a list that will contain the meshes of the scene
    """
    itemType = lx.eval('query sceneservice item.type ? {0}'.format(selectedObject))
    if itemType == 'groupLocator':
        getAllChildrenMeshes(object,meshList)
    
    elif itemType == 'mesh':
        meshList.append(selectedObject)

def showDialog(title, msg, msgType):
    """Shows a dialog, the info inf this dialog is defined by the args
    Args:
        title: a str containing the info for the dialog's title
        msg: a str with the message
        msgType: the options for the dialog
    returns
        the answer of the user
    """
    try:
        lx.eval('dialog.setup {0}'.format(msgType))
        lx.eval('dialog.title {0}'.format(title))
        lx.eval('dialog.msg {0}'.format(msg))
        lx.eval('dialog.result ok')
        lx.eval('dialog.open')
        result = lx.eval('dialog.result ?')
        return result
        
    except:
        result = lx.eval('dialog.result ?')
        return result

def sourceMel():
    HOST = '127.0.0.1' # the local host
    PORT = 5055 # The same port openedd in maya, ie, commandPort -n ":5055";
    ADDR=(HOST,PORT)
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    #
    command = 'source "/the/path/where/your/maya/scripts/are/ToMaya.mel";'#or put ToMaya.mel in a valid path of MAYA_SCRIPTS_PATH
    
    client.send(command)
    data = client.recv(1024) #receive the result info
    client.close()

    print 'The Result is {0}'.format(data)
    
exportMeshes()