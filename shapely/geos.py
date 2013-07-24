"""
Proxies for the libgeos_c shared lib, GEOS-specific exceptions, and utilities
"""

import os
import re
import sys
import atexit
import ctypes
import logging
import threading
from ctypes import CDLL, cdll, pointer, c_void_p, c_size_t, c_char_p, string_at
from ctypes.util import find_library

from . import ftools
from .ctypes_declarations import prototype, EXCEPTION_HANDLER_FUNCTYPE



# Begin by creating a do-nothing handler and adding to this module's logger.
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
LOG = logging.getLogger(__name__)
LOG.addHandler(NullHandler())

# Find and load the GEOS and C libraries
# If this ever gets any longer, we'll break it into separate modules

def load_dll(libname, fallbacks=None):
    lib = find_library(libname)
    if lib is not None:
        return CDLL(lib)
    else:
        if fallbacks is not None:
            for name in fallbacks:
                try:
                    return CDLL(name)
                except OSError:
                    # move on to the next fallback
                    pass
        # the end
        raise OSError(
            "Could not find library %s or load any of its variants %s" % (
                libname, fallbacks or []))

if sys.platform.startswith('linux'):
    _lgeos = load_dll('geos_c', fallbacks=['libgeos_c.so.1', 'libgeos_c.so'])
    free = load_dll('c').free
    free.argtypes = [c_void_p]
    free.restype = None

elif sys.platform == 'darwin':
    alt_paths = [
            # The Framework build from Kyng Chaos:
            "/Library/Frameworks/GEOS.framework/Versions/Current/GEOS",
            # macports
            '/opt/local/lib/libgeos_c.dylib',
    ]
    _lgeos = load_dll('geos_c', fallbacks=alt_paths)
    free = load_dll('c').free
    free.argtypes = [c_void_p]
    free.restype = None

elif sys.platform == 'win32':
    try:
        egg_dlls = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                     r"DLLs"))
        wininst_dlls =  os.path.abspath(os.__file__ + "../../../DLLs")
        original_path = os.environ['PATH']
        os.environ['PATH'] = "%s;%s;%s" % (egg_dlls, wininst_dlls, original_path)
        _lgeos = CDLL("geos.dll")
    except (ImportError, WindowsError, OSError):
        raise
    def free(m):
        try:
            cdll.msvcrt.free(m)
        except WindowsError:
            # XXX: See http://trac.gispython.org/projects/PCL/ticket/149
            pass

elif sys.platform == 'sunos5':
    _lgeos = load_dll('geos_c', fallbacks=['libgeos_c.so.1', 'libgeos_c.so'])
    free = CDLL('libc.so.1').free
    free.argtypes = [c_void_p]
    free.restype = None

else: # other *nix systems
    _lgeos = load_dll('geos_c', fallbacks=['libgeos_c.so.1', 'libgeos_c.so'])
    free = load_dll('c', fallbacks=['libc.so.6']).free
    free.argtypes = [c_void_p]
    free.restype = None

def _geos_version():
    # extern const char GEOS_DLL *GEOSversion();
    GEOSversion = _lgeos.GEOSversion
    GEOSversion.restype = c_char_p
    GEOSversion.argtypes = []
    #define GEOS_CAPI_VERSION "@VERSION@-CAPI-@CAPI_VERSION@"
    geos_version_string = GEOSversion()
    if sys.version_info[0] >= 3:
        geos_version_string = geos_version_string.decode('ascii')
    res = re.findall(r'(\d+)\.(\d+)\.(\d+)', geos_version_string)
    assert len(res) == 2, res
    geos_version = tuple(int(x) for x in res[0])
    capi_version = tuple(int(x) for x in res[1])
    return geos_version_string, geos_version, capi_version

geos_version_string, geos_version, geos_capi_version = _geos_version()

# If we have the new interface, then record a baseline so that we know what
# additional functions are declared in ctypes_declarations.
if geos_version >= (3, 1, 0):
    start_set = set(_lgeos.__dict__)

# Apply prototypes for the libgeos_c functions
prototype(_lgeos, geos_version)

# If we have the new interface, automatically detect all function
# declarations, and declare their re-entrant counterpart.
if geos_version >= (3, 1, 0):
    end_set = set(_lgeos.__dict__)
    new_func_names = end_set - start_set

    for func_name in new_func_names:
        new_func_name = "%s_r" % func_name
        if hasattr(_lgeos, new_func_name):
            new_func = getattr(_lgeos, new_func_name)
            old_func = getattr(_lgeos, func_name)
            new_func.restype = old_func.restype
            if old_func.argtypes is None:
                # Handle functions that didn't take an argument before,
                # finishGEOS.
                new_func.argtypes = [c_void_p]
            else:
                new_func.argtypes = [c_void_p] + old_func.argtypes
            if old_func.errcheck is not None:
                new_func.errcheck = old_func.errcheck

    # Handle special case.
    _lgeos.initGEOS_r.restype = c_void_p
    _lgeos.initGEOS_r.argtypes = [EXCEPTION_HANDLER_FUNCTYPE, EXCEPTION_HANDLER_FUNCTYPE]
    _lgeos.finishGEOS_r.argtypes = [c_void_p]

# Exceptions

class ReadingError(Exception):
    pass

class DimensionError(Exception):
    pass

class TopologicalError(Exception):
    pass

class PredicateError(Exception):
    pass

def error_handler(fmt, list):
    LOG.error("%s", list)
error_h = EXCEPTION_HANDLER_FUNCTYPE(error_handler)

def notice_handler(fmt, list):
    LOG.warning("%s", list)
notice_h = EXCEPTION_HANDLER_FUNCTYPE(notice_handler)


class WKTReader(object):

    def __init__(self, lgeos):
        """Create WKT Reader"""
        self._lgeos = lgeos
        self.__reader__ = self._lgeos.GEOSWKTReader_create()

    def __del__(self):
        """Destroy WKT Reader"""
        if self._lgeos is not None:
            self._lgeos.GEOSWKTReader_destroy(self.__reader__)
            self.__reader__ = None
            self._lgeos = None

    def read(self, text):
        """Returns geometry from WKT"""
        if sys.version_info[0] >= 3:
            text = text.encode('ascii')
        geom = self._lgeos.GEOSWKTReader_read(self.__reader__, c_char_p(text))
        if not geom:
            raise ReadingError("Could not create geometry because of errors "
                               "while reading input.")
        # avoid circular import dependency
        from shapely import geometry
        return geometry.base.geom_factory(geom)


class WKTWriter(object):

    def __init__(self, lgeos):
        """Create WKT Writer

        Note: writer defaults are set differently for GEOS 3.3.0 and up.
        For example, with 'POINT Z (1 2 3)':

            newer: POINT Z (1 2 3)
            older: POINT (1.0000000000000000 2.0000000000000000)

        The older formatting can be achieved for GEOS 3.3.0 and up by setting
        the properties:
            trim = False
            output_dimension = 2
        """
        self._lgeos = lgeos
        self.__writer__ = self._lgeos.GEOSWKTWriter_create()
        if self._lgeos.geos_version >= (3, 3, 0):
            # Establish defaults
            self.trim = True
            self.output_dimension = 3

    def __del__(self):
        """Destroy WKT Writer"""
        if self._lgeos is not None:
            self._lgeos.GEOSWKTWriter_destroy(self.__writer__)
            self.__writer__ = None
            self._lgeos = None

    def write(self, geom):
        """Returns WKT for geometry"""
        if geom is None or geom._geom is None:
            raise ValueError("Null geometry supports no operations")
        result = self._lgeos.GEOSWKTWriter_write(self.__writer__, geom._geom)
        text = string_at(result)
        lgeos.GEOSFree(result)
        if sys.version_info[0] >= 3:
            return text.decode('ascii')
        else:
            return text

    if geos_version >= (3, 3, 0):

        @property
        def trim(self):
            """Trimming of unnecessary decimals (default: True)"""
            return getattr(self, '_trim', False)

        @trim.setter
        def trim(self, value):
            self._trim = bool(value)
            self._lgeos.GEOSWKTWriter_setTrim(self.__writer__, self._trim)

        @property
        def rounding_precision(self):
            """Rounding precision when writing the WKT.
            A precision of -1 (default) disables it."""
            return getattr(self, '_rounding_precision', -1)

        @rounding_precision.setter
        def rounding_precision(self, value):
            self._rounding_precision = int(value)
            self._lgeos.GEOSWKTWriter_setRoundingPrecision(
                                self.__writer__, self._rounding_precision)

        @property
        def output_dimension(self):
            """Output dimension, either 2 or 3 (default)"""
            return self._lgeos.GEOSWKTWriter_getOutputDimension(
                                self.__writer__)

        @output_dimension.setter
        def output_dimension(self, value):
            self._lgeos.GEOSWKTWriter_setOutputDimension(
                                self.__writer__, int(value))


class WKBReader(object):

    def __init__(self, lgeos):
        """Create WKB Reader"""
        self._lgeos = lgeos
        self.__reader__ = self._lgeos.GEOSWKBReader_create()

    def __del__(self):
        """Destroy WKB Reader"""
        if self._lgeos is not None:
            self._lgeos.GEOSWKBReader_destroy(self.__reader__)
            self.__reader__ = None
            self._lgeos = None

    def read(self, data):
        """Returns geometry from WKB"""
        geom = self._lgeos.GEOSWKBReader_read(
                        self.__reader__, c_char_p(data), c_size_t(len(data)))
        if not geom:
            raise ReadingError("Could not create geometry because of errors "
                               "while reading input.")
        # avoid circular import dependency
        from shapely import geometry
        return geometry.base.geom_factory(geom)

    def read_hex(self, data):
        """Returns geometry from WKB hex"""
        if sys.version_info[0] >= 3:
            data = data.encode('ascii')
        geom = self._lgeos.GEOSWKBReader_readHEX(
                        self.__reader__, c_char_p(data), c_size_t(len(data)))
        if not geom:
            raise ReadingError("Could not create geometry because of errors "
                               "while reading input.")
        # avoid circular import dependency
        from shapely import geometry
        return geometry.base.geom_factory(geom)


class WKBWriter(object):

    def __init__(self, lgeos):
        """Create WKB Writer"""
        self._lgeos = lgeos
        self.__writer__ = self._lgeos.GEOSWKBWriter_create()
        # Establish defaults
        self.output_dimension = 3

    def __del__(self):
        """Destroy WKB Writer"""
        if self._lgeos is not None:
            self._lgeos.GEOSWKBWriter_destroy(self.__writer__)
            self.__writer__ = None
            self._lgeos = None

    def write(self, geom):
        """Returns WKB for geometry"""
        if geom is None or geom._geom is None:
            raise ValueError("Null geometry supports no operations")
        size = c_size_t()
        result = self._lgeos.GEOSWKBWriter_write(
                        self.__writer__, geom._geom, pointer(size))
        data = string_at(result, size.value)
        lgeos.GEOSFree(result)
        return data

    def write_hex(self, geom):
        """Returns WKB hex for geometry"""
        if geom is None or geom._geom is None:
            raise ValueError("Null geometry supports no operations")
        size = c_size_t()
        result = self._lgeos.GEOSWKBWriter_writeHEX(
                        self.__writer__, geom._geom, pointer(size))
        data = string_at(result, size.value)
        lgeos.GEOSFree(result)
        if sys.version_info[0] >= 3:
            return data.decode('ascii')
        else:
            return data

    @property
    def output_dimension(self):
        """Output dimension, either 2 or 3 (default)"""
        return self._lgeos.GEOSWKBWriter_getOutputDimension(self.__writer__)

    @output_dimension.setter
    def output_dimension(self, value):
        self._lgeos.GEOSWKBWriter_setOutputDimension(
                            self.__writer__, int(value))

    @property
    def big_endian(self):
        """Byte order is big endian, True (default) or False"""
        return bool(self._lgeos.GEOSWKBWriter_getByteOrder(self.__writer__))

    @big_endian.setter
    def big_endian(self, value):
        self._lgeos.GEOSWKBWriter_setByteOrder(self.__writer__, bool(value))

    @property
    def include_srid(self):
        """Include SRID, True or False (default)"""
        return bool(self._lgeos.GEOSWKBWriter_getIncludeSRID(self.__writer__))

    @include_srid.setter
    def include_srid(self, value):
        self._lgeos.GEOSWKBWriter_setIncludeSRID(self.__writer__, bool(value))


# Errcheck functions for ctypes

def errcheck_wkb(result, func, argtuple):
    '''Returns bytes from a C pointer'''
    if not result:
        return None
    size_ref = argtuple[-1]
    size = size_ref.contents
    retval = ctypes.string_at(result, size.value)[:]
    lgeos.GEOSFree(result)
    return retval

def errcheck_just_free(result, func, argtuple):
    '''Returns string from a C pointer'''
    retval = string_at(result)
    lgeos.GEOSFree(result)
    if sys.version_info[0] >= 3:
        return retval.decode('ascii')
    else:
        return retval

def errcheck_predicate(result, func, argtuple):
    '''Result is 2 on exception, 1 on True, 0 on False'''
    if result == 2:
        raise PredicateError("Failed to evaluate %s" % repr(func))
    return result


class LGEOSBase(threading.local):
    """Proxy for GEOS C API

    This is a base class. Do not instantiate.
    """
    methods = {}
    def __init__(self, dll):
        self._lgeos = dll
        self.geos_handle = None

    def __del__(self):
        """Cleanup GEOS related processes"""
        self.wkt_reader.__del__()
        self.wkt_writer.__del__()
        self.wkb_reader.__del__()
        self.wkb_writer.__del__()
        if self._lgeos is not None:
            self._lgeos.finishGEOS()
            self._lgeos = None
            self.geos_handle = None


class LGEOS300(LGEOSBase):
    """Proxy for GEOS 3.0.0-CAPI-1.4.1
    """
    geos_version = (3, 0, 0)
    geos_capi_version = (1, 4, 0)
    def __init__(self, dll):
        super(LGEOS300, self).__init__(dll)
        self.geos_handle = self._lgeos.initGEOS(notice_h, error_h)
        keys = list(self._lgeos.__dict__.keys())
        for key in keys:
            setattr(self, key, getattr(self._lgeos, key))
        self.GEOSFree = self._lgeos.free
        # Deprecated
        self.GEOSGeomToWKB_buf.errcheck = errcheck_wkb
        self.GEOSGeomToWKT.errcheck = errcheck_just_free
        #
        self.wkt_reader = WKTReader(self)
        self.wkt_writer = WKTWriter(self)
        self.wkb_reader = WKBReader(self)
        self.wkb_writer = WKBWriter(self)
        self.GEOSRelate.errcheck = errcheck_just_free
        for pred in ( self.GEOSDisjoint,
              self.GEOSTouches,
              self.GEOSIntersects,
              self.GEOSCrosses,
              self.GEOSWithin,
              self.GEOSContains,
              self.GEOSOverlaps,
              self.GEOSEquals,
              self.GEOSEqualsExact,
              self.GEOSisEmpty,
              self.GEOSisValid,
              self.GEOSisSimple,
              self.GEOSisRing,
              self.GEOSHasZ
              ):
            pred.errcheck = errcheck_predicate

        self.methods['area'] = self.GEOSArea
        self.methods['boundary'] = self.GEOSBoundary
        self.methods['buffer'] = self.GEOSBuffer
        self.methods['centroid'] = self.GEOSGetCentroid
        self.methods['representative_point'] = self.GEOSPointOnSurface
        self.methods['convex_hull'] = self.GEOSConvexHull
        self.methods['distance'] = self.GEOSDistance
        self.methods['envelope'] = self.GEOSEnvelope
        self.methods['length'] = self.GEOSLength
        self.methods['has_z'] = self.GEOSHasZ
        self.methods['is_empty'] = self.GEOSisEmpty
        self.methods['is_ring'] = self.GEOSisRing
        self.methods['is_simple'] = self.GEOSisSimple
        self.methods['is_valid'] = self.GEOSisValid
        self.methods['disjoint'] = self.GEOSDisjoint
        self.methods['touches'] = self.GEOSTouches
        self.methods['intersects'] = self.GEOSIntersects
        self.methods['crosses'] = self.GEOSCrosses
        self.methods['within'] = self.GEOSWithin
        self.methods['contains'] = self.GEOSContains
        self.methods['overlaps'] = self.GEOSOverlaps
        self.methods['equals'] = self.GEOSEquals
        self.methods['equals_exact'] = self.GEOSEqualsExact
        self.methods['relate'] = self.GEOSRelate
        self.methods['difference'] = self.GEOSDifference
        self.methods['symmetric_difference'] = self.GEOSSymDifference
        self.methods['union'] = self.GEOSUnion
        self.methods['intersection'] = self.GEOSIntersection
        self.methods['simplify'] = self.GEOSSimplify
        self.methods['topology_preserve_simplify'] = \
            self.GEOSTopologyPreserveSimplify


class LGEOS310(LGEOSBase):
    """Proxy for GEOS 3.1.0-CAPI-1.5.0
    """
    geos_version = (3, 1, 0)
    geos_capi_version = (1, 5, 0)
    def __init__(self, dll):
        super(LGEOS310, self).__init__(dll)
        self.geos_handle = self._lgeos.initGEOS_r(notice_h, error_h)
        keys = list(self._lgeos.__dict__.keys())
        for key in [x for x in keys if not x.endswith('_r')]:
            if key + '_r' in keys:
                reentr_func = getattr(self._lgeos, key + '_r')
                attr = ftools.partial(reentr_func, self.geos_handle)
                attr.__name__ = reentr_func.__name__
                setattr(self, key, attr)
            else:
                setattr(self, key, getattr(self._lgeos, key))
        if not hasattr(self, 'GEOSFree'):
            # GEOS < 3.1.1
            self.GEOSFree = self._lgeos.free
        # Deprecated
        self.GEOSGeomToWKB_buf.func.errcheck = errcheck_wkb
        self.GEOSGeomToWKT.func.errcheck = errcheck_just_free
        #
        self.wkt_reader = WKTReader(self)
        self.wkt_writer = WKTWriter(self)
        self.wkb_reader = WKBReader(self)
        self.wkb_writer = WKBWriter(self)
        self.GEOSRelate.func.errcheck = errcheck_just_free
        for pred in ( self.GEOSDisjoint,
              self.GEOSTouches,
              self.GEOSIntersects,
              self.GEOSCrosses,
              self.GEOSWithin,
              self.GEOSContains,
              self.GEOSOverlaps,
              self.GEOSEquals,
              self.GEOSEqualsExact,
              self.GEOSisEmpty,
              self.GEOSisValid,
              self.GEOSisSimple,
              self.GEOSisRing,
              self.GEOSHasZ
              ):
            pred.func.errcheck = errcheck_predicate

        self.GEOSisValidReason.func.errcheck = errcheck_just_free

        self.methods['area'] = self.GEOSArea
        self.methods['boundary'] = self.GEOSBoundary
        self.methods['buffer'] = self.GEOSBuffer
        self.methods['centroid'] = self.GEOSGetCentroid
        self.methods['representative_point'] = self.GEOSPointOnSurface
        self.methods['convex_hull'] = self.GEOSConvexHull
        self.methods['distance'] = self.GEOSDistance
        self.methods['envelope'] = self.GEOSEnvelope
        self.methods['length'] = self.GEOSLength
        self.methods['has_z'] = self.GEOSHasZ
        self.methods['is_empty'] = self.GEOSisEmpty
        self.methods['is_ring'] = self.GEOSisRing
        self.methods['is_simple'] = self.GEOSisSimple
        self.methods['is_valid'] = self.GEOSisValid
        self.methods['disjoint'] = self.GEOSDisjoint
        self.methods['touches'] = self.GEOSTouches
        self.methods['intersects'] = self.GEOSIntersects
        self.methods['crosses'] = self.GEOSCrosses
        self.methods['within'] = self.GEOSWithin
        self.methods['contains'] = self.GEOSContains
        self.methods['overlaps'] = self.GEOSOverlaps
        self.methods['equals'] = self.GEOSEquals
        self.methods['equals_exact'] = self.GEOSEqualsExact
        self.methods['relate'] = self.GEOSRelate
        self.methods['difference'] = self.GEOSDifference
        self.methods['symmetric_difference'] = self.GEOSSymDifference
        self.methods['union'] = self.GEOSUnion
        self.methods['intersection'] = self.GEOSIntersection
        self.methods['prepared_intersects'] = self.GEOSPreparedIntersects
        self.methods['prepared_contains'] = self.GEOSPreparedContains
        self.methods['prepared_contains_properly'] = \
            self.GEOSPreparedContainsProperly
        self.methods['prepared_covers'] = self.GEOSPreparedCovers
        self.methods['simplify'] = self.GEOSSimplify
        self.methods['topology_preserve_simplify'] = \
            self.GEOSTopologyPreserveSimplify
        self.methods['cascaded_union'] = self.GEOSUnionCascaded


class LGEOS311(LGEOS310):
    """Proxy for GEOS 3.1.1-CAPI-1.6.0
    """
    geos_version = (3, 1, 1)
    geos_capi_version = (1, 6, 0)
    def __init__(self, dll):
        super(LGEOS311, self).__init__(dll)


class LGEOS320(LGEOS311):
    """Proxy for GEOS 3.2.0-CAPI-1.6.0
    """
    geos_version = (3, 2, 0)
    geos_capi_version = (1, 6, 0)
    def __init__(self, dll):
        super(LGEOS320, self).__init__(dll)

        self.methods['parallel_offset'] = self.GEOSSingleSidedBuffer
        self.methods['project'] = self.GEOSProject
        self.methods['project_normalized'] = self.GEOSProjectNormalized
        self.methods['interpolate'] = self.GEOSInterpolate
        self.methods['interpolate_normalized'] = \
            self.GEOSInterpolateNormalized


class LGEOS330(LGEOS320):
    """Proxy for GEOS 3.3.0-CAPI-1.7.0
    """
    geos_version = (3, 3, 0)
    geos_capi_version = (1, 7, 0)
    def __init__(self, dll):
        super(LGEOS330, self).__init__(dll)

        self.methods['unary_union'] = self.GEOSUnaryUnion
        self.methods['cascaded_union'] = self.methods['unary_union']


if geos_version >= (3, 3, 0):
    L = LGEOS330
elif geos_version >= (3, 2, 0):
    L = LGEOS320
elif geos_version >= (3, 1, 1):
    L = LGEOS311
elif geos_version >= (3, 1, 0):
    L = LGEOS310
else:
    L = LGEOS300

lgeos = L(_lgeos)


@atexit.register
def cleanup():
    lgeos.__del__()
