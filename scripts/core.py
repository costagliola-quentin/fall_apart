import hou


def createNull():
    """Creates a Null node at the output of the selected node."""
    def getOutputWires(node):
        result = []
        for i in node.outputs():
            result.append(i)
            result += getOutputWires(i)
        return result


    slection = hou.selectedNodes()
    if slection == ():
        hou.ui.displayMessage("select node please")
    else:
        ### "sel" = dernier noeud dans la liste des noeuds sÃƒÂ©lectionnÃƒÂ©s
        sel = slection[-1]
        down_conn = sel.outputConnections()
        all_down = getOutputWires(sel)

        ### Bouge tous les noeuds "getOutputWires" de 1 vers le bas
        for i in all_down:
            i.move((0, -1))

        ### "par" = le noeud parent, celui qui va crÃƒÂ©er le nouveau nul
        par = sel.parent()
        nul = par.createNode(node_type_name="null", node_name='OUT')
        ### Positionne le nul -1 sous "sel"
        nul.setPosition(sel.position() - hou.Vector2(0, 1))
        ### connect
        nul.setInput(0, sel)
        ### color
        nul.setColor(hou.Color((.85, .1, 00)))

        ### RÃƒÂ©tablit les connections en dessous de "sel"
        for i in down_conn:
            i.outputNode().setInput(i.inputIndex(), nul, 0)


def switchCooking():
    """Switches cooking on or off."""
    mode = hou.updateModeSetting().name()

    if mode == 'AutoUpdate':
        hou.setUpdateMode(hou.updateMode.Manual)
    if mode == 'Manual':
        hou.setUpdateMode(hou.updateMode.AutoUpdate)


def connectNode():
    """Connect nodes, from A to B."""
    inputs = hou.selectedNodes()[1:]
    target = hou.selectedNodes()[0]
    target_con = len(target.inputConnections())
    for count, node in enumerate(inputs):
        target.setInput(count + target_con, node)


def objectMerge():
    """ Creates an object merge node linked to the selected object."""
    sel = hou.selectedNodes()

    if len(sel) == 1:
        curPath = sel[0].parent()
        objPath = sel[0].path()
        pos = sel[0].position() + hou.Vector2(0, -1)

        mkMerge = curPath.createNode("object_merge")
        mkMerge.setPosition(pos)
        try:
            mkMerge.setName(sel[0].name() + "_merge")
        except:
            mkMerge.setName(sel[0].name() + "_merge1")
        mkMerge.parm("xformtype").set(1)
        mkMerge.parm("objpath1").set(objPath)


def objectMergeIn():
    pass


def objectMergeOut():
    pass
