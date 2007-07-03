from ctypes import string_at, byref, c_int, c_size_t, c_char_p, c_double
    #, create_string_buffer \
    #, c_char_p, c_double, c_float, c_int, c_uint, c_size_t, c_ubyte \
    #, c_void_p, byref

from shapely.geos import lgeos
from shapely.geos import BinaryPredicate, UnaryPredicate
from shapely.geos import OperationError


def geom_factory(g):
    ob = BaseGeometry()
    geom_type = string_at(lgeos.GEOSGeomType(g))
    mod = __import__(
        'shapely.geometry', 
        globals(), 
        locals(), 
        [geom_type],
        )
    ob.__class__ = getattr(mod, geom_type)
    ob._geom = g
    return ob


class BaseGeometry(object):
    
    """Defines methods common to all geometries.
    """

    _geom = None
    _ctypes_data = None
    _ndim = None
    _crs = None

    def __init__(self):
        self._geom = lgeos.GEOSGeomFromWKT(c_char_p('GEOMETRYCOLLECTION EMPTY'))

    def __del__(self):
        if self._geom is not None:
            lgeos.GEOSGeom_destroy(self._geom)

    def __str__(self):
        return self.to_wkt()

    def __reduce__(self):
        return (self.__class__, (), self.to_wkb())

    def __setstate__(self, state):
        self._geom = lgeos.GEOSGeomFromWKB_buf(
                        c_char_p(state), 
                        c_size_t(len(state))
                        )

    # Array and ctypes interfaces

    @property
    def array(self):
        """Return a GeoJSON coordinate array.
        
        To be overridden by extension classes."""
        raise NotImplemented

    @property
    def ctypes(self):
        """Return a ctypes representation.
        
        To be overridden by extension classes."""
        raise NotImplemented

    @property
    def __array_interface__(self):
        """Provide the Numpy array protocol."""
        return {
            'version': 3,
            'shape': (self._ndim,),
            'typestr': '>f8',
            'data': self.ctypes
            }

    # Python feature protocol

    @property
    def type(self):
        return self.geometryType()

    @property
    def coordinates(self):
        return self.array


    def geometryType(self):
        """Returns a string representing the geometry type, e.g. 'Polygon'."""
        return string_at(lgeos.GEOSGeomType(self._geom))

    def to_wkb(self):
        """Returns a WKT string representation of the geometry."""
        size = c_int()
        bytes = lgeos.GEOSGeomToWKB_buf(self._geom, byref(size))
        return string_at(bytes, size.value)

    def to_wkt(self):
        """Returns a WKT string representation of the geometry."""
        return string_at(lgeos.GEOSGeomToWKT(self._geom))

    # Properties
    geom_type = property(geometryType)
    wkt = property(to_wkt)
    wkb = property(to_wkb)

    # Topology operations
    
    @property
    def envelope(self):
        return geom_factory(lgeos.GEOSEnvelope(self._geom))

    def intersection(self, other):
        return geom_factory(lgeos.GEOSEnvelope(self._geom, other._geom))

    def buffer(self, distance, quadsegs=16):
        return geom_factory(
            lgeos.GEOSBuffer(self._geom, c_double(distance), c_int(quadsegs))
            )

    @property
    def convex_hull(self):
        return geom_factory(lgeos.GEOSConvexHull(self._geom))

    def difference(self, other):
        return geom_factory(lgeos.GEOSDifference(self._geom, other._geom))

    def symmetric_difference(self, other):
        return geom_factory(lgeos.GEOSSymDifference(self._geom, other._geom))

    @property
    def boundary(self):
        return geom_factory(lgeos.GEOSBoundary(self._geom))

    def union(self, other):
        return geom_factory(lgeos.GEOSUnion(self._geom, other._geom))

    @property
    def centroid(self):
        return geom_factory(lgeos.GEOSGetCentroid(self._geom))

    def relate(self, other):
        func = lgeos.GEOSRelate
        func.restype = c_char_p
        return lgeos.GEOSRelate(self._geom, other._geom)

    # Binary predicates

    # Relate Pattern (TODO?)
    disjoint = BinaryPredicate(lgeos.GEOSDisjoint)
    touches = BinaryPredicate(lgeos.GEOSTouches)
    intersects = BinaryPredicate(lgeos.GEOSIntersects)
    crosses = BinaryPredicate(lgeos.GEOSCrosses)
    within = BinaryPredicate(lgeos.GEOSWithin)
    contains = BinaryPredicate(lgeos.GEOSContains)
    overlaps = BinaryPredicate(lgeos.GEOSOverlaps)
    equals = BinaryPredicate(lgeos.GEOSEquals)

    # Unary predicates

    is_empty = UnaryPredicate(lgeos.GEOSisEmpty)
    is_valid = UnaryPredicate(lgeos.GEOSisValid)
    is_simple = UnaryPredicate(lgeos.GEOSisSimple)
    is_ring = UnaryPredicate(lgeos.GEOSisRing)
    has_z = UnaryPredicate(lgeos.GEOSHasZ)

