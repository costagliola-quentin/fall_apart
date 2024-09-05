import hou


def createNull():
    """Creates a Null node at the output of the selected node.
    Hotkey: F12"""
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
        sel = slection[-1]
        down_conn = sel.outputConnections()
        all_down = getOutputWires(sel)

        ### Moves all the "getOutputWires" nodes of 1 unit down.
        for i in all_down:
            i.move((0, -1))

        ### "par" = the parent node, the one creating the new null
        par = sel.parent()
        nul = par.createNode(node_type_name="null", node_name='OUT')
        nul.setPosition(sel.position() - hou.Vector2(0, 1))
        nul.setInput(0, sel)
        nul.setColor(hou.Color((.85, .1, 00)))

        ### Reset all the connections before sel
        for i in down_conn:
            i.outputNode().setInput(i.inputIndex(), nul, 0)


def switchCooking():
    """Switches cooking on or off.
    Hotkey: Ctrl + E"""
    mode = hou.updateModeSetting().name()

    if mode == 'AutoUpdate':
        hou.setUpdateMode(hou.updateMode.Manual)
    if mode == 'Manual':
        hou.setUpdateMode(hou.updateMode.AutoUpdate)


def connectNode():
    """Connect nodes, from A to B.
    Hotkey: Alt + E"""
    inputs = hou.selectedNodes()[1:]
    target = hou.selectedNodes()[0]
    target_con = len(target.inputConnections())
    for count, node in enumerate(inputs):
        target.setInput(count + target_con, node)


def objectMerge():
    """ Creates an object merge node linked to the selected object.
    Hotkey: Ctrl + Alt + E"""
    sel = hou.selectedNodes()

    if len(sel) == 1:
        curPath = sel[0].parent()
        objPath = sel[0].path()
        pos = sel[0].position() + hou.Vector2(0, -1)

        mkMerge = curPath.createNode("object_merge")
        mkMerge.setPosition(pos)
        try:
            mkMerge.setName("merge_" + sel[0].name())
        except:
            mkMerge.setName("merge_" + sel[0].name() + "1")
        mkMerge.parm("xformtype").set(1)
        mkMerge.parm("objpath1").set(objPath)


def objectMergeIn():
    pass


def objectMergeOut():
    pass


def unplugNodeInputOutput():
    """Unplug a node from its inputs and outputs
    Hotkey: Alt + E"""
    sel = hou.selectedNodes()

    if sel == ():
        print('You have to select at least one node!')
    else:
        for node in sel:
            # Unplug all input connections
            for i in range(len(node.inputConnections())):
                node.setInput(i, None)

            # Unplug all output connections
            output_connections = node.outputConnections()
            for conn in output_connections:
                output_node = conn.outputNode()
                output_node.setInput(conn.inputIndex(), None)