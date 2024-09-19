import hou, os


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
    Hotkey: Ctrl + Shift + E"""
    inputs = hou.selectedNodes()[1:]
    target = hou.selectedNodes()[0]
    target_con = len(target.inputConnections())
    for count, node in enumerate(inputs):
        target.setInput(count + target_con, node)


def objectMerge():
    """ Creates an object merge node linked to the selected object.
    Hotkey: Alt + Shift + E"""
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


def createFileCache():
    """Creates a labs_file_cache, and a fall_apart_preview, set default parms if needed."""

    # Create labs filecache after selection
    sel = hou.selectedNodes()
    sel = sel[-1]
    filecache = sel.createOutputNode("labs::filecache")
    filecache.parm('basename').set('`opname("..")`_`$OS`')
    filecache.parm('hardenbasename').set(0)
    filecache.parm('tpostrender').set(1)
    reload_str = """hou.parm(hou.pwd()+'/reload').pressButton()"""
    filecache.parm('postrender').setExpression(reload_str, hou.exprLanguage.Python)
    filecache.parm('lpostrender').set('python')

    pass


class FallApartCache():
    """
    OUTDATED !
    """

    @staticmethod
    def updateCachePath(kwargs):

        node = kwargs['node']

        # node.parm('extension').pressButton()
        directory = node.evalParm('directory')
        cache_name = node.evalParm('cache_name')
        extension = node.parm('extension').evalAsString()

        frame_range = node.parm('frame_range').evalAsString()
        frame = ''
        if frame_range != 'single':
            frame = '.$F4'

        node.parm('cache_path').set(os.path.join(directory, cache_name + frame + extension))

    @staticmethod
    def executeRenderGeometry(kwargs):
        node = kwargs['node']

        enable_wedge = node.evalParm('enable_wedge')

        if not enable_wedge:
            node.parm('executeRenderGeometry').pressButton()
        else:
            pass


    @staticmethod
    def executeOpenglPreview(kwargs):
        print("Execute opengl preview")

        cache_node = kwargs['node']
        # filecache_node = hou.node(preview_node.evalParm('labs_file_cache_to_preview'))
        # hou.node('./ropnet1/opengl1').parm('execute').pressButton()


    @staticmethod
    def executeBuildMosaic(kwargs):
        print("Execute build mosaic")


    @staticmethod
    def executeBuildVideo(kwargs):
        print("Execute Build MP4")

    @staticmethod
    def execute(kwargs):
        print("\nExecute IN")

        node = kwargs['node']

        enable_wedge = node.evalParm('enable_wedge')

        is_geo_enabled = node.evalParm('write_geometry')
        is_preview_enabled = node.evalParm('render_opengl')
        is_mosaic_enabled = node.evalParm('render_mosaic')
        is_video_enabled = node.evalParm('render_mp4')






        if is_geo_enabled:


            pass
        if is_preview_enabled:
            pass
        if is_mosaic_enabled:
            pass
        if is_video_enabled:
            pass

        print("Execute OUT")







































