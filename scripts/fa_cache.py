import re
import os
import shutil
from logging import raiseExceptions

import hou, nodegraphtopui
from enum import Enum
from imp import reload
from . import utils
reload(utils)


def callback(function):
    """Creating decorator for callback functions."""
    def wrapper(*args, **kwargs):
        return_value = function(*args, **kwargs)
        # print('Callback function triggered.')
        return return_value

    return wrapper


def evaluation(function):
    """Creating decorator for evaluation functions."""
    def wrapper(*args, **kwargs):
        return_value = function(*args, **kwargs)
        return return_value

    return wrapper


@callback
def onCreated(kwargs):
    """Callback created when the fa_cache node is created."""
    node = kwargs['node']
    node.setColor(hou.Color(0.29, 0.565, 0.886))


@callback
def setToLastVersion(kwargs):
    """Sets the version slider to the last version that exists on disk."""
    node = kwargs['node']
    geo_cache_folder = node.evalParm('geometry_cache_folder')
    children_folders = os.listdir(geo_cache_folder)
    v_list = []
    for child in children_folders:
        if re.match(r"""^v\d*$""", child):
            child = child[1:]
            v_list.append(int(child))

    max_ver = max(*v_list) if len(v_list) > 1 else 1
    node.parm('version').set(max_ver)
    return max_ver


@callback
def incrementVersion(kwargs):
    """Gets the last existing version and adds 1."""
    last_ver = setToLastVersion(kwargs)
    kwargs['node'].parm('version').set(last_ver + 1)


@callback
def deleteVersion(kwargs):
    """Deletes the current version if it exists and after user confirmation."""
    node = kwargs['node']
    curr_version = node.evalParm('version_string')
    folders = [
        node.evalParm('geometry_cache_folder') + r'/' + curr_version,
        node.evalParm('image_cache_folder') + r'/' + curr_version
    ]

    if not node.evalParm('enable_version') :
        hou.ui.displayMessage('Versioning is disabled.')
        return

    # test if the current version exists !
    if not os.access(folders[0], os.F_OK) or os.access(folders[1], os.F_OK):
        hou.ui.displayMessage('There are no files corresponding to this version.', severity=hou.severityType.Error)
        return


    message = ('This is going to DELETE every cached geometry and renders for the current version. '
               '\n\nAre you sure?')
    if not hou.ui.displayConfirmation(message):
        return

    for folder in folders:
        try:
            shutil.rmtree(folder)
            hou.ui.displayMessage('Folder and its content removed')
            return
        except:
            hou.ui.displayMessage('Something wrong happened, folder not deleted', severity=hou.severityType.Error)
            return



@callback
def deleteEverything(kwargs):
    """Deletes the content of the geometry_cache_folder and image_cache_folder, after user confirmation."""
    node = kwargs['node']
    folders = [
        node.evalParm('geometry_cache_folder'),
        node.evalParm('image_cache_folder')
    ]

    message = ('This is going to DELETE every cached geometry and renders for every versions.'
               '\n\nAre you sure?')
    if hou.ui.displayConfirmation(message):
        for folder in folders:
            try:
                if not os.access(folder, os.F_OK):
                    raise Exception()
                shutil.rmtree(folder)
                hou.ui.displayMessage('Folder and its content removed')
            except Exception as e:
                print(e)
                hou.ui.displayMessage('Something wrong happened, folder not deleted')
    else:
        return


@callback
def saveToDisk(kwargs):
    """CALLBACK: Triggered when 'Save to Disk' button is pressed. Triggers the top_network OUT node."""

    node = kwargs['node']
    top_node = node.node('./top_network')

    # CHECK AUTO VERSION
    if node.evalParm('enable_version') and node.evalParm('enable_auto_version'):
        if os.access(node.evalParm('geometry_cache_folder'), os.F_OK):
            incrementVersion(kwargs)
        else:
            node.parm('version').set(1)

    # CHECK WEDGING
    if node.evalParm('enable_wedging'):
        top_node.node('Wedges').setGenericFlag(hou.nodeFlag.Bypass, False)
    else:
        top_node.node('Wedges').setGenericFlag(hou.nodeFlag.Bypass, True)

    # HANDLE STRIP
    strip_parm = node.parm('enable_strip')
    strip_evaluated_value = strip_parm.eval()

    # SET MOSAIC STRIP OFF IF WEDGING IS OFF
    button_index = 3
    if node.evalParm('enable_wedging'):
        node.parm('bypass_render_mosaic').set(0)
        new_value = strip_evaluated_value | (1 << button_index)
        strip_parm.set(new_value)
        # top_node.node('render_mosaic').setGenericFlag(hou.nodeFlag.Bypass, True)
    else :
        new_value = strip_evaluated_value & ~(1 << button_index)
        strip_parm.set(new_value)
        node.parm('bypass_render_mosaic').set(1)
#         top_node.node('render_mosaic').setGenericFlag(hou.nodeFlag.Bypass, False)

    # ANALYSE OF BTN STRIP
    strip_state = []
    strip_evaluated_value = strip_parm.eval()
    for i in range(5):
        state = (strip_evaluated_value >> i) & 1
        strip_state.append(1 if state == 1 else 0)

    cache_mode_parms = [
        'pdg_cachemode_render_geo',
        'pdg_cachemode_render_opengl',
        'pdg_cachemode_render_overlay',
        'pdg_cachemode_render_mosaic',
        'pdg_cachemode_render_video'
    ]

    for i in range(0, len(cache_mode_parms), 1):
        i_parm = node.parm(cache_mode_parms[i])
        i_node = top_node.node('./'+cache_mode_parms[i].replace('pdg_cachemode_', ''))
        if strip_state[i]:
            # Render
            i_parm.set(2)
            i_node.setColor(hou.Color(0.302, 0.525, 0.114))
        else:
            # Don't render
            i_parm.set(1)
            i_node.setColor(hou.Color(0.71, 0.518, 0.004))

    nodegraphtopui.dirtyAll(node.parm('target_top_network').evalAsNode(), False)
    nodegraphtopui.cookOutputNode(node.parm('target_top_network').evalAsNode())


@callback
def createWedgeNode(kwargs):
    """CALLBACK: Creates a wedge node inside the 'top_network/Wedges' folder."""
    node = kwargs['node']
    in_wedge = node.node('./top_network/Wedges/IN_WEDGES')
    out_cons = in_wedge.outputConnections()

    new_wedge = in_wedge.createOutputNode('wedge')
    new_wedge.setColor(hou.Color(0.451, 0.369, 0.796))

    for i in out_cons:
        i.outputNode().setInput(i.inputIndex(), new_wedge, 0)

    # Dive inside the node in the network view
    network_editors = [pane for pane in hou.ui.paneTabs() if isinstance(pane, hou.NetworkEditor)]
    network_editor = None
    if network_editors:
        network_editor = network_editors[0]

    network_editor.setCurrentNode(new_wedge)

    node.node('./top_network/Wedges').layoutChildren()


@callback
def task(kwargs):
    """CALLBACK: Triggered when the user updates the 'task' parm to update the 'video_cache_name' parm."""
    node = kwargs['node']
    node.cook(True)
    node.parm('video_cache_name').pressButton()


class OutputFileType(Enum):
    """Defines an enum that represents the whole types of render that fa_cache can do."""
    GEOMETRY = 0
    RENDER = 1
    OVERLAY = 2
    MOSAIC = 3
    VIDEO = 4


@evaluation
def getCacheName(node, output_type):
    """EVALUATION: Sets the '{OutputFileType}_cache_name' parms values."""
    node = hou.pwd()

    base_name = node.evalParm('base_name')
    version = '_' + node.evalParm('version_string') if node.evalParm('enable_version') else ''
    wedge = '_' + node.evalParm('wedge_string') if node.evalParm('enable_wedging') else ''
    frame = node.evalParm('frame_string') if node.evalParm('time_dependent_cache') else ''
    geometry_ext = node.parm('extension').evalAsString()
    if geometry_ext == '0':
        geometry_ext = '.bgeo.sc'
    else:
        geometry_ext = '.vdb'
    task = utils.fix_string(node.evalParm('task'))
    task = '_' + task if task else ''


    if output_type == OutputFileType.GEOMETRY:
        return f'{base_name}{version}{wedge}{frame}{geometry_ext}'
    elif output_type == OutputFileType.RENDER:
        return f'{base_name}{version}{wedge}{frame}.png'
    elif output_type == OutputFileType.OVERLAY:
        return f'{base_name}{version}{wedge}{frame}.png'
    elif output_type == OutputFileType.MOSAIC:
        return f'{base_name}{version}{frame}.png'
    elif output_type == OutputFileType.VIDEO:
        return f'{base_name}{version}{task}.mp4'


@evaluation
def getOutputFile(node, output_type):
    """EVALUATION: Sets the '{OutputFileType}_output_file' parms values."""

    geo_cache_folder = node.evalParm('geometry_cache_folder')
    image_cache_folder = node.evalParm('image_cache_folder')
    cache_name = None
    version = '/' + node.evalParm('version_string') if node.evalParm('enable_version') else ''
    wedge = '/' + node.evalParm('wedge_string') if node.evalParm('enable_wedging') else ''
    # frame = node.evalParm('frame_string')

    if output_type == OutputFileType.GEOMETRY:
        cache_name = node.evalParm('geometry_cache_name')
        return f'{geo_cache_folder}{version}{wedge}/{cache_name}'
    elif output_type == OutputFileType.RENDER:
        cache_name = node.evalParm('render_cache_name')
        return f'{image_cache_folder}{version}/render_opengl{wedge}/{cache_name}'
    elif output_type == OutputFileType.OVERLAY:
        cache_name = node.evalParm('overlay_cache_name')
        return f'{image_cache_folder}{version}/overlay{wedge}/{cache_name}'
    elif output_type == OutputFileType.MOSAIC:
        cache_name = node.evalParm('mosaic_cache_name')
        return f'{image_cache_folder}{version}/mosaic{wedge}/{cache_name}'
    elif output_type == OutputFileType.VIDEO:
        cache_name = node.evalParm('video_cache_name')
        return f'{image_cache_folder}/{cache_name}'
    else:
        return 0


@callback
def openTopNetwork(kwargs):
    """CALLBACK: Triggered when 'open_top_network_btn' is pressed."""
    desktop = hou.ui.curDesktop()
    new_pane = desktop.createFloatingPane(hou.paneTabType.NetworkEditor)
    node = kwargs['node'].node('top_network/Wedges')
    # new_pane.pwd(node)
    new_pane.setCurrentNode(node)


@callback
def open_base_folder(kwargs):
    """Opens the base_folder."""
    path = kwargs['node'].evalParm('base_folder')
    if os.access(path, os.F_OK):
        # utils.open_explorer(path)
        os.startfile(path)


@callback
def open_base_render_folder(kwargs):
    """Opens the base_render_folder"""
    path = kwargs['node'].evalParm('base_render_folder')
    if os.access(path, os.F_OK):
        os.startfile(path)


@callback
def open(kwargs):
    """Triggered by one of the open_<outputFileType> button"""

    node = kwargs['node']
    button = kwargs['parm_name']
    file = True if node.parm('open_menu').evalAsString() == 'open_file' else False # if file == false, it's a folder then.
    print(file)
    print(kwargs)

    path = None
    if button == 'open_geometry':
        path = node.evalParm('geometry_output_file') if file else getOutputFile(node, OutputFileType.GEOMETRY)
    elif button == 'open_render':
        path = node.evalParm('render_output_file') if file else getOutputFile(node, OutputFileType.RENDER)
    elif button == 'open_overlay':
        path = node.evalParm('overlay_output_file') if file else getOutputFile(node, OutputFileType.OVERLAY)
    elif button == 'open_mosaic':
        path = node.evalParm('mosaic_output_file') if file else getOutputFile(node, OutputFileType.MOSAIC)
    elif button == 'open_video':
        path = node.evalParm('video_output_file') if file else getOutputFile(node, OutputFileType.VIDEO)

    if file:
        try:
            os.startfile(path)
        except FileNotFoundError:
            message = """File does not exist. Make sure it has been properly rendered"""
            hou.ui.displayMessage(message, severity=hou.severityType.Error)
    else:
        if os.access(path, os.F_OK):
            utils.open_explorer(path)
        else:
            message = """Folder does not exist. Make sure its content has been properly rendered"""
            hou.ui.displayMessage(message, severity=hou.severityType.Error)


@callback
def timeDependentCache(kwargs):
    """Triggered when user changes time_dependent_cache toggle value.
    Updates the trange"""
    node = kwargs['node']
    time_dep = kwargs['script_value']
    if time_dep == 'on':
        node.parm('trange').set(1)
    else:
        node.parm('trange').set(0)





























