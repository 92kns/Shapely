"""
"""

from ctypes import string_at, create_string_buffer, \
    c_char_p, c_double, c_float, c_int, c_uint, c_size_t, c_ubyte, \
    c_void_p, byref
from ctypes import cast, POINTER

from shapely.geos import lgeos, DimensionError
from shapely.geometry.base import BaseGeometry

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

    def __init__(self, *args):
        """Initialize a point.
        
        Parameters
        ----------
        
        There are 2 cases:

        1) 1 parameter: this must satisfy the numpy array protocol.
        2) 2 or more parameters: x, y, z : float
            Easting, northing, and elevation.
        """
        BaseGeometry.__init__(self)

        if len(args) == 0:
            # allow creation of null points, to support unpickling
            pass
        else:
            if len(args) == 1:
                # From array protocol
                array = args[0].__array_interface__
                n = array['shape'][0]
                assert n == 2 or n == 3

                cdata = array['data'][0]
                cp = cast(cdata, POINTER(c_double))
                dx = c_double(cp[0])
                dy = c_double(cp[1])
                dz = None
                ndim = 2
                if n == 3:
                    dz = c_double(cp[2])
                    ndim = 3
            else:
                # x, y, (z) parameters
                dx = c_double(args[0])
                dy = c_double(args[1])
                dz = None
                ndim = 2
                if len(args) >= 3:
                    dz = c_double(args[2])
                    ndim = 3
    
            self._ndim = ndim

            cs = lgeos.GEOSCoordSeq_create(1, ndim)
            # Because of a bug in the GEOS C API, always set X before Y
            lgeos.GEOSCoordSeq_setX(cs, 0, dx)
            lgeos.GEOSCoordSeq_setY(cs, 0, dy)
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

        # First because of a GEOS C API bug, save Y
        dy = c_double()
        lgeos.GEOSCoordSeq_getY(cs, 0, byref(dy))
        
        if self._ndim == 3:
            dz = c_double()
            lgeos.GEOSCoordSeq_getZ(cs, 0, byref(dz))
        
        lgeos.GEOSCoordSeq_setX(cs, 0, c_double(x))

        # Now, restore Y. Yuck.
        lgeos.GEOSCoordSeq_setY(cs, 0, dy)

        if self._ndim == 3:
            lgeos.GEOSCoordSeq_setZ(cs, 0, dz)
    
    def getY(self):
        """Return y coordinate."""
        cs = lgeos.GEOSGeom_getCoordSeq(self._geom)
        d = c_double()
        lgeos.GEOSCoordSeq_getY(cs, 0, byref(d))
        return d.value
    
    def setY(self, y):
        """Set y coordinate."""
        cs = lgeos.GEOSGeom_getCoordSeq(self._geom)

        if self._ndim == 3:
            # First because of a GEOS C API bug, save Z
            d = c_double()
            lgeos.GEOSCoordSeq_getZ(cs, 0, byref(d))
        
            lgeos.GEOSCoordSeq_setY(cs, 0, c_double(y))
        
            # Now, restore Z. Yuck.
            lgeos.GEOSCoordSeq_setZ(cs, 0, d)
        else:
            lgeos.GEOSCoordSeq_setY(cs, 0, c_double(y))

    def getZ(self):
        """Return z coordinate."""
        if self._ndim != 3:
            raise DimensionError, "This point has no z coordinate."
        cs = lgeos.GEOSGeom_getCoordSeq(self._geom)
        d = c_double()
        lgeos.GEOSCoordSeq_getZ(cs, 0, byref(d))
        return d.value
    
    def setZ(self, z):
        """Set z coordinate."""
        if self._ndim != 3:
            raise DimensionError, "This point has no z coordinate."
        cs = lgeos.GEOSGeom_getCoordSeq(self._geom)
        lgeos.GEOSCoordSeq_setZ(cs, 0, c_double(z))
    
    # Coordinate properties
    x = property(getX, setX)
    y = property(getY, setY)
    z = property(getZ, setZ)

    @property
    def array(self):
        """Return a GeoJSON coordinate array."""
        array = [self.x, self.y]
        if self._ndim == 3: # TODO: use hasz
            array.append(self.z)
        return array

    @property
    def ctypes(self):
        if not self._ctypes_data:
            if self._ndim == 3: # TODO: use hasz
                array = c_double * 3
                self._ctypes_data = array(self.x, self.y, self.z)
            else:
                array = c_double * 2
                self._ctypes_data = array(self.x, self.y)
        return self._ctypes_data


# Test runner
def _test():
    import doctest
    doctest.testmod()


if __name__ == "__main__":
    _test()

