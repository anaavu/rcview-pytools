"""Various classes and functions for working with GIS data."""

import os as _os
import urllib as _urllib
import mgrs as _mgrs
import numpy as _numpy
from .constants import OS_WINDOWS, IN_IPYTHON
from halo import Halo as _Halo
from arcgis.gis import Item


def round_significant(x, p=2):
    """Round positive numeric value to significant digits.

    Arguments:
    x  A numeric value.
    p  Significant digits precision.
    """
    if x == 0.0:
        return x
    elif x < 0:
        raise ValueError('Value must be positive.')
    else:
        return _numpy.around(x, -int(_numpy.floor(_numpy.log10(x))) + (p - 1))


def fix_fgdb_files(dir):
    """Fix ESRI file geodatabase file names.

    Sometimes a windows-style directory name is prepended to each file name.
    This function strips that directory name from each file.
    Arguments:
    dir  Directory containing the geodatabase files.
    """
    _os.chdir(dir)
    for file in _os.listdir():
        _os.rename(file, file.split('\\')[1])


def google_maps_url(latitude, longitude):
    """Google Maps URL for a point location.

    Arguments:
    latitude   Latitude in decimal degrees.
    longitude  Longitude in decimal degrees.
    """
    return 'https://www.google.com/maps/place/{0:2.5f},{1:3.5f}/@{0:2.5f},{1:3.5f},18z'.\
        format(latitude, longitude)


def apple_maps_url(latitude, longitude, label='X'):
    """Apple Maps URL for a point location.

    Arguments:
    latitude   Latitude in decimal degrees.
    longitude  Longitude in decimal degrees.
    label      Text label for map point.
    """
    return 'http://maps.apple.com/?ll={0:2.5f},{1:3.5f}&q={2:s}'.format(
        latitude, longitude, _urllib.parse.quote(label))


def latlon_to_usng(latitude, longitude, precision=4):
    """US National Grid value for a point location.

    The precision argument can range from 0 to 5, with 5 representing a 1-m
    grid, 4 a 10-m grid, 3 a 100-m grid, and so on.
    Arguments:
    latitude   Latitude in decimal degrees.
    longitude  Longitude in decimal degrees.
    precision  Grid value precision.
    """
    m = _mgrs.MGRS()
    usng = m.toMGRS(latitude, longitude, MGRSPrecision=precision).decode('ascii')
    usng_fmt = []
    usng_fmt.append(usng[0:3])
    usng_fmt.append(usng[3:5])
    if precision > 0:
        gc =  usng[5:]
        idx_split = int(len(gc) / 2)
        usng_fmt.append(gc[0:idx_split])
        usng_fmt.append(gc[idx_split:])
    return ' '.join(usng_fmt)


def usng_to_latlon(usng):
    """Latitude and longitude for a US National Grid location.

    Returns a tuple with latitude and longitude in decimal degrees.
    Arguments:
    usng  A US National Grid value.
    """
    m = _mgrs.MGRS()
    return m.toLatLon(usng.replace(' ', '').encode('ascii'))


if IN_IPYTHON:
    # Halo spinners presently do not work in IPython and Jupyter Notebooks.
    from IPython.display import display, HTML, clear_output
    import uuid
    class RCActivityIndicator():
        """An activity indicator."""
        def __init__(self, text='Processing'):
            """Construct a Red Cross activity indicator.

            Arguments:
            text  The text to display next to the indicator.
            """
            self._symbol = '<font color="red">✚</font>'
            self._active = False
            self._text = text
            self._display = None
        def start(self):
            self._active = True
            if not self._display:
                self._display = display(self._display_text,
                                        display_id=uuid.uuid4().hex)
            else:
                self._print()
        def stop(self):
            self._active = False
            clear_output()
        def stop_and_persist(self):
            self._active = False
            self._print()
        def succeed(self, text):
            self._active = False
            self._symbol = '<font color="green">✔︎</font>'
            self._text = text
            self._print()
        def fail(self, text):
            self._active = False
            self._symbol = '<font color="red">✖︎</font>'
            self._text = text
            self._print()
        def warn(self, text):
            self._active = False
            self._symbol = '<font color="gold">⚠︎︎︎</font>'
            self._text = text
            self._print()
        def _print(self):
            self._display.update(self._display_text)
        @property
        def text(self):
            return self._text
        @text.setter
        def text(self, value):
            self._text = value
            self._print()
        @property
        def _display_text(self):
            return HTML('{} <i>{}{}</i>'.format(
                self._symbol, self._text, '…' if self._active else ''))

else:
    class RCActivityIndicator(_Halo):
        """An activity indicator."""
        def __init__(self, text='Processing'):
            """Construct a Red Cross activity indicator.

            Arguments:
            text  The text to display next to the indicator.
            """
            super().__init__(
                text=text,
                spinner=\
                    {'interval': 200, 'frames': [' ', '.', '+', '.']} if OS_WINDOWS \
                    else {'interval': 200, 'frames': ['∙', '+', '✛', '✚', '✛', '+']},
                color='red'
            )


def _patched_copy_feature_layer_collection(self, service_name, layers=None,
                                           tables=None, folder=None,
                                           description=None, snippet=None, owner=None):
    """
    This operation allows users to copy existing Feature Layer Collections and select the
    layers/tables that the user wants in the service.
    NOTE: This is a patched version that correctly sets the new service item's name.
    ==================     ====================================================================
    **Argument**           **Description**
    ------------------     --------------------------------------------------------------------
    service_name           Required string. It is the name of the service.
    ------------------     --------------------------------------------------------------------
    layers                 Optional list/string.  This is a either a list of integers or a comma
                            seperated list of integers as a string.  Each index value represents
                            a layer in the feature layer collection.
    ------------------     --------------------------------------------------------------------
    tables                 Optional list/string. This is a either a list of integers or a comma
                            seperated list of integers as a string.  Each index value represents
                            a table in the feature layer collection.
    ------------------     --------------------------------------------------------------------
    folder                 Optional string. This is the name of the folder to place in.  The
                            default is None, which means the root folder.
    ------------------     --------------------------------------------------------------------
    description            Optional string. This is the Item description of the service.
    ------------------     --------------------------------------------------------------------
    snippet                Optional string. This is the Item's snippet of the service. It is
                            no longer than 250 characters.
    ------------------     --------------------------------------------------------------------
    owner                  Optional string/User. The default is the current user, but if you
                            want the service to be owned by another user, pass in this value.
    ==================     ====================================================================


    :return:
        Item on success. None on failure

    """
    from arcgis.features import FeatureLayerCollection
    if self.type != "Feature Service" and \
        self.type != "Feature Layer Collection":
        return
    if layers is None and tables is None:
        raise ValueError("An index of layers or tables must be provided")
    content = self._gis.content
    if isinstance(owner, User):
        owner = owner.username
    idx_layers = []
    idx_tables = []
    params = {}
    allowed = ['description', 'allowGeometryUpdates', 'units', 'syncEnabled',
               'serviceDescription', 'capabilities', '_ssl',
               'supportsDisconnectedEditing', 'maxRecordCount',
               'supportsApplyEditsWithGlobalIds', 'supportedQueryFormats',
               'xssPreventionInfo', 'copyrightText', 'currentVersion',
               'syncCapabilities', 'hasStaticData', 'hasVersionedData',
               'editorTrackingInfo']
    parent = None
    if description is None:
        description = self.description
    if snippet is None:
        snippet = self.snippet
    i = 1
    is_free = content.is_service_name_available(service_name=service_name,
                                                service_type="Feature Service")
    if is_free == False:
        while is_free == False:
            i += 1
            s = service_name + "_%s" % i
            is_free = content.is_service_name_available(service_name=s,
                                                        service_type="Feature Service")
            if is_free:
                service_name = s
                break
    if len(self.tables) > 0 or len(self.layers) > 0:
        parent = FeatureLayerCollection(url=self.url, gis=self._gis)
    else:
        raise Exception("No tables or layers found in service, cannot copy it.")
    if layers is not None:
        if isinstance(layers, (list, tuple)):
            for idx in layers:
                idx_layers.append(self.layers[idx])
                del idx
        elif isinstance(layers, (str)):
            for idx in layers.split(','):
                idx_layers.append(self.layers[idx])
                del idx
        else:
            raise ValueError("layers must be a comma seperated list of integers or a list")
    if tables is not None:
        if isinstance(tables, (list, tuple)):
            for idx in tables:
                idx_tables.append(self.tables[idx])
                del idx
        elif isinstance(tables, (str)):
            for idx in tables.split(','):
                idx_tables.append(self.tables[idx])
                del idx
        else:
            raise ValueError("tables must be a comma seperated list of integers or a list")
    for k, v in dict(parent.properties).items():
        if k in allowed:
            params[k] = v
    params['name'] = service_name
    #print('DEBUG: service_name: ' + service_name, flush=True)
    #print('DEBUG: params:', flush=True)
    #pp(params)
    copied_item = content.create_service(name=service_name,
                                            create_params=params,
                                            folder=folder,
                                            owner=owner,
                                            item_properties={'description':description,
                                                            'snippet': snippet,
                                                            'tags' : self.tags,
                                                            'title' : service_name
                                                            })

    fs = FeatureLayerCollection(url=copied_item.url, gis=self._gis)
    fs_manager = fs.manager
    add_defs = {'layers' : [], 'tables' : []}
    for l in idx_layers:
        v = dict(l.manager.properties)
        if 'indexes' in v:
            del v['indexes']
        if 'adminLayerInfo' in v:
            del v['adminLayerInfo']
        add_defs['layers'].append(v)
        del l
    for l in idx_tables:
        v = dict(l.manager.properties)
        if 'indexes' in v:
            del v['indexes']
        if 'adminLayerInfo' in v:
            del v['adminLayerInfo']
        add_defs['tables'].append(v)
        del l
    res = fs_manager.add_to_definition(json_dict=add_defs)
    if res['success'] ==  True:
        return copied_item
    else:
        try:
            copied_item.delete()
        except: pass
    return None

Item.copy_feature_layer_collection = _patched_copy_feature_layer_collection
