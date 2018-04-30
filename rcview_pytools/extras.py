"""Various classes and functions for working with GIS data."""

import os as _os
import urllib as _urllib
import mgrs as _mgrs
import numpy as _numpy
from .constants import OS_WINDOWS
from halo import Halo as _Halo


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


class RCSpinner(_Halo):
    """An activity spinner with a pulsating red cross."""
    def __init__(self, text='Processing'):
        """Construct a Red Cross spinner.

        Arguments:
        text  The text to display next to the spinner.
        """
        super().__init__(
            text=text,
            spinner=\
                {'interval': 200, 'frames': [' ', '.', '+', '.']} if OS_WINDOWS \
                else {'interval': 200, 'frames': ['∙', '+', '✛', '✚', '✛', '+']},
            color='red'
        )
