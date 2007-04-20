"""
"""

from ctypes import string_at, create_string_buffer, \
    c_char_p, c_double, c_float, c_int, c_uint, c_size_t, c_ubyte, \
    c_void_p, byref

from geos import lgeos, GEOSError, DimensionError
from base import BaseGeometry

class Point(BaseGeometry):

    """A point geometry.
    
    Attributes
    ----------
    x, y, z : float
        Coordinate values

    Example
    -------
    >>> p = Point(1.0, -1.0)
    >>> str(p)
    'POINT (1.0000000000000000 -1.0000000000000000)'
    >>> p.y = 0.0
    >>> p.y
    0.0
    >>> p.x
    1.0
    >>> p.array
    [[1.0, 0.0]]
    """

    def __init__(self, x=None, y=None, z=None, crs=None):
        """Initialize a point.
        
        Parameters
        ----------
        x, y, z : float
            Easting, northing, and elevation.
        crs : string
            PROJ.4 representation of a coordinate system.
        """
        BaseGeometry.__init__(self)

        # check coordinate input
        dx = c_double(x)
        dy = c_double(y)
        try:
            dz = c_double(z)
            ndim = 3
        except TypeError:
            dz = None
            ndim = 2
    
        self._geom = None
        self._ndim = ndim
        self._crs = crs

        cs = lgeos.GEOSCoordSeq_create(1, ndim)
        # XXX: setting X appears to clobber Y. Watch how the doctest above
        # fails.
        lgeos.GEOSCoordSeq_setY(cs, 0, dy)
        lgeos.GEOSCoordSeq_setX(cs, 0, dx)
        if ndim == 3:
            lgeos.GEOSCoordSeq_setZ(cs, 0, dz)
        
        self._geom = lgeos.GEOSGeom_createPoint(cs)

    # Coordinate getters and setters

    def getX(self):
        """Return x coordinate."""
        cs = lgeos.GEOSGeom_getCoordSeq(self._geom)
        d = c_double()
        lgeos.GEOSCoordSeq_getX(cs, 0, byref(d))
        return d.value
    
    def setX(self, x):
        """Set x coordinate."""
        cs = lgeos.GEOSGeom_getCoordSeq(self._geom)
        lgeos.GEOSCoordSeq_setX(cs, 0, c_double(x))
    
    def getY(self):
        """Return y coordinate."""
        cs = lgeos.GEOSGeom_getCoordSeq(self._geom)
        d = c_double()
        lgeos.GEOSCoordSeq_getY(cs, 0, byref(d))
        return d.value
    
    def setY(self, y):
        """Set y coordinate."""
        cs = lgeos.GEOSGeom_getCoordSeq(self._geom)
        lgeos.GEOSCoordSeq_setY(cs, 0, c_double(y))
    
    def getZ(self):
        """Return z coordinate."""
        if self._ndim != 3:
            raise DimensionError, \
            "This point has no z coordinate."
        cs = lgeos.GEOSGeom_getCoordSeq(self._geom)
        d = c_double()
        lgeos.GEOSCoordSeq_getZ(cs, 0, byref(d))
        return d.value
    
    def setZ(self, z):
        """Set z coordinate."""
        if self._ndim != 3:
            raise DimensionError, \
            "This point has no z coordinate."
        cs = lgeos.GEOSGeom_getCoordSeq(self._geom)
        lgeos.GEOSCoordSeq_setZ(cs, 0, c_double(z))
    
    # Coordinate properties
    x = property(getX, setX)
    y = property(getY, setY)
    z = property(getZ, setZ)

    def toarray(self):
        """Return a GeoJSON coordinate array."""
        inner = [self.x, self.y]
        if self._ndim == 3: # TODO: use hasz
            inner.append(self.z)
        return [inner]
    
    array = property(toarray)


# Test runner
def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()

