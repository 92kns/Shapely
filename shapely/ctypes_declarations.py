# Prototyping of libgeos_c functions, now using a function written by
# `tartley`: http://trac.gispython.org/lab/ticket/189

from ctypes import CFUNCTYPE, POINTER, c_void_p, c_char_p, \
    c_size_t, c_byte, c_char, c_uint, c_int, c_double


class allocated_c_char_p(c_char_p):
    pass

EXCEPTION_HANDLER_FUNCTYPE = CFUNCTYPE(None, c_char_p, c_char_p)


def prototype(lgeos, geosVersion):

    lgeos.initGEOS.restype = None
    lgeos.initGEOS.argtypes = [EXCEPTION_HANDLER_FUNCTYPE, EXCEPTION_HANDLER_FUNCTYPE]

    lgeos.finishGEOS.restype = None
    lgeos.finishGEOS.argtypes = []

    lgeos.GEOSversion.restype = c_char_p
    lgeos.GEOSversion.argtypes = []

    lgeos.GEOSGeomFromWKT.restype = c_void_p
    lgeos.GEOSGeomFromWKT.argtypes = [c_char_p]

    lgeos.GEOSGeomToWKT.restype = allocated_c_char_p
    lgeos.GEOSGeomToWKT.argtypes = [c_void_p]

    lgeos.GEOS_setWKBOutputDims.restype = c_int
    lgeos.GEOS_setWKBOutputDims.argtypes = [c_int]

    lgeos.GEOSGeomFromWKB_buf.restype = c_void_p
    lgeos.GEOSGeomFromWKB_buf.argtypes = [c_void_p, c_size_t]

    lgeos.GEOSGeomToWKB_buf.restype = allocated_c_char_p
    lgeos.GEOSGeomToWKB_buf.argtypes = [c_void_p, POINTER(c_size_t)]

    lgeos.GEOSCoordSeq_create.restype = c_void_p
    lgeos.GEOSCoordSeq_create.argtypes = [c_uint, c_uint]

    lgeos.GEOSCoordSeq_clone.restype = c_void_p
    lgeos.GEOSCoordSeq_clone.argtypes = [c_void_p]

    lgeos.GEOSCoordSeq_destroy.restype = None
    lgeos.GEOSCoordSeq_destroy.argtypes = [c_void_p]

    lgeos.GEOSCoordSeq_setX.restype = c_int
    lgeos.GEOSCoordSeq_setX.argtypes = [c_void_p, c_uint, c_double]

    lgeos.GEOSCoordSeq_setY.restype = c_int
    lgeos.GEOSCoordSeq_setY.argtypes = [c_void_p, c_uint, c_double]

    lgeos.GEOSCoordSeq_setZ.restype = c_int
    lgeos.GEOSCoordSeq_setZ.argtypes = [c_void_p, c_uint, c_double]

    lgeos.GEOSCoordSeq_setOrdinate.restype = c_int
    lgeos.GEOSCoordSeq_setOrdinate.argtypes = [c_void_p, c_uint, c_uint, c_double]

    lgeos.GEOSCoordSeq_getX.restype = c_int
    lgeos.GEOSCoordSeq_getX.argtypes = [c_void_p, c_uint, c_void_p]

    lgeos.GEOSCoordSeq_getY.restype = c_int
    lgeos.GEOSCoordSeq_getY.argtypes = [c_void_p, c_uint, c_void_p]

    lgeos.GEOSCoordSeq_getZ.restype = c_int
    lgeos.GEOSCoordSeq_getZ.argtypes = [c_void_p, c_uint, c_void_p]

    lgeos.GEOSCoordSeq_getSize.restype = c_int
    lgeos.GEOSCoordSeq_getSize.argtypes = [c_void_p, c_void_p]

    lgeos.GEOSCoordSeq_getDimensions.restype = c_int
    lgeos.GEOSCoordSeq_getDimensions.argtypes = [c_void_p, c_void_p]

    lgeos.GEOSGeom_createPoint.restype = c_void_p
    lgeos.GEOSGeom_createPoint.argtypes = [c_void_p]

    lgeos.GEOSGeom_createLinearRing.restype = c_void_p
    lgeos.GEOSGeom_createLinearRing.argtypes = [c_void_p]

    lgeos.GEOSGeom_createLineString.restype = c_void_p
    lgeos.GEOSGeom_createLineString.argtypes = [c_void_p]

    lgeos.GEOSGeom_createPolygon.restype = c_void_p
    lgeos.GEOSGeom_createPolygon.argtypes = [c_void_p, c_void_p, c_uint]

    lgeos.GEOSGeom_createCollection.restype = c_void_p
    lgeos.GEOSGeom_createCollection.argtypes = [c_int, c_void_p, c_uint]

    lgeos.GEOSGeom_clone.restype = c_void_p
    lgeos.GEOSGeom_clone.argtypes = [c_void_p]

    lgeos.GEOSGeom_destroy.restype = None
    lgeos.GEOSGeom_destroy.argtypes = [c_void_p]

    lgeos.GEOSEnvelope.restype = c_void_p
    lgeos.GEOSEnvelope.argtypes = [c_void_p]

    lgeos.GEOSIntersection.restype = c_void_p
    lgeos.GEOSIntersection.argtypes = [c_void_p, c_void_p]

    lgeos.GEOSBuffer.restype = c_void_p
    lgeos.GEOSBuffer.argtypes = [c_void_p, c_double, c_int]

    lgeos.GEOSSimplify.restype = c_void_p
    lgeos.GEOSSimplify.argtypes = [c_void_p, c_double]

    lgeos.GEOSTopologyPreserveSimplify.restype = c_void_p
    lgeos.GEOSTopologyPreserveSimplify.argtypes = [c_void_p, c_double]

    lgeos.GEOSConvexHull.restype = c_void_p
    lgeos.GEOSConvexHull.argtypes = [c_void_p]

    lgeos.GEOSDifference.restype = c_void_p
    lgeos.GEOSDifference.argtypes = [c_void_p, c_void_p]

    lgeos.GEOSSymDifference.restype = c_void_p
    lgeos.GEOSSymDifference.argtypes = [c_void_p, c_void_p]

    lgeos.GEOSBoundary.restype = c_void_p
    lgeos.GEOSBoundary.argtypes = [c_void_p]

    lgeos.GEOSUnion.restype = c_void_p
    lgeos.GEOSUnion.argtypes = [c_void_p, c_void_p]

    lgeos.GEOSPointOnSurface.restype = c_void_p
    lgeos.GEOSPointOnSurface.argtypes = [c_void_p]

    lgeos.GEOSGetCentroid.restype = c_void_p
    lgeos.GEOSGetCentroid.argtypes = [c_void_p]

    lgeos.GEOSRelate.restype = allocated_c_char_p
    lgeos.GEOSRelate.argtypes = [c_void_p, c_void_p]

    lgeos.GEOSPolygonize.restype = c_void_p
    lgeos.GEOSPolygonize.argtypes = [c_void_p, c_uint]

    lgeos.GEOSLineMerge.restype = c_void_p
    lgeos.GEOSLineMerge.argtypes = [c_void_p]

    lgeos.GEOSRelatePattern.restype = c_char
    lgeos.GEOSRelatePattern.argtypes = [c_void_p, c_void_p, c_char_p]

    lgeos.GEOSDisjoint.restype = c_byte
    lgeos.GEOSDisjoint.argtypes = [c_void_p, c_void_p]

    lgeos.GEOSTouches.restype = c_byte
    lgeos.GEOSTouches.argtypes = [c_void_p, c_void_p]

    lgeos.GEOSIntersects.restype = c_byte
    lgeos.GEOSIntersects.argtypes = [c_void_p, c_void_p]

    lgeos.GEOSCrosses.restype = c_byte
    lgeos.GEOSCrosses.argtypes = [c_void_p, c_void_p]

    lgeos.GEOSWithin.restype = c_byte
    lgeos.GEOSWithin.argtypes = [c_void_p, c_void_p]

    lgeos.GEOSContains.restype = c_byte
    lgeos.GEOSContains.argtypes = [c_void_p, c_void_p]

    lgeos.GEOSOverlaps.restype = c_byte
    lgeos.GEOSOverlaps.argtypes = [c_void_p, c_void_p]

    lgeos.GEOSEquals.restype = c_byte
    lgeos.GEOSEquals.argtypes = [c_void_p, c_void_p]

    lgeos.GEOSEqualsExact.restype = c_byte
    lgeos.GEOSEqualsExact.argtypes = [c_void_p, c_void_p, c_double]

    lgeos.GEOSisEmpty.restype = c_byte
    lgeos.GEOSisEmpty.argtypes = [c_void_p]

    lgeos.GEOSisValid.restype = c_byte
    lgeos.GEOSisValid.argtypes = [c_void_p]

    lgeos.GEOSisSimple.restype = c_byte
    lgeos.GEOSisSimple.argtypes = [c_void_p]

    lgeos.GEOSisRing.restype = c_byte
    lgeos.GEOSisRing.argtypes = [c_void_p]

    lgeos.GEOSHasZ.restype = c_byte
    lgeos.GEOSHasZ.argtypes = [c_void_p]

    lgeos.GEOSGeomType.restype = c_char_p
    lgeos.GEOSGeomType.argtypes = [c_void_p]

    lgeos.GEOSGeomTypeId.restype = c_int
    lgeos.GEOSGeomTypeId.argtypes = [c_void_p]

    lgeos.GEOSGetSRID.restype = c_int
    lgeos.GEOSGetSRID.argtypes = [c_void_p]

    lgeos.GEOSSetSRID.restype = None
    lgeos.GEOSSetSRID.argtypes = [c_void_p, c_int]

    lgeos.GEOSGetNumGeometries.restype = c_int
    lgeos.GEOSGetNumGeometries.argtypes = [c_void_p]

    lgeos.GEOSGetGeometryN.restype = c_void_p
    lgeos.GEOSGetGeometryN.argtypes = [c_void_p, c_int]

    lgeos.GEOSGetNumInteriorRings.restype = c_int
    lgeos.GEOSGetNumInteriorRings.argtypes = [c_void_p]

    lgeos.GEOSGetInteriorRingN.restype = c_void_p
    lgeos.GEOSGetInteriorRingN.argtypes = [c_void_p, c_int]

    lgeos.GEOSGetExteriorRing.restype = c_void_p
    lgeos.GEOSGetExteriorRing.argtypes = [c_void_p]

    lgeos.GEOSGetNumCoordinates.restype = c_int
    lgeos.GEOSGetNumCoordinates.argtypes = [c_void_p]

    lgeos.GEOSGeom_getCoordSeq.restype = c_void_p
    lgeos.GEOSGeom_getCoordSeq.argtypes = [c_void_p]

    lgeos.GEOSGeom_getDimensions.restype = c_int
    lgeos.GEOSGeom_getDimensions.argtypes = [c_void_p]

    lgeos.GEOSArea.restype = c_double
    lgeos.GEOSArea.argtypes = [c_void_p, c_void_p]

    lgeos.GEOSLength.restype = c_int
    lgeos.GEOSLength.argtypes = [c_void_p, c_void_p]

    lgeos.GEOSDistance.restype = c_int
    lgeos.GEOSDistance.argtypes = [c_void_p, c_void_p, c_void_p]

    if geosVersion >= (1, 5, 0):

        if hasattr(lgeos, 'GEOSFree'):
            lgeos.GEOSFree.restype = None
            lgeos.GEOSFree.argtypes = [c_void_p]

        # Prepared geometry, GEOS C API 1.5.0+
        lgeos.GEOSPrepare.restype = c_void_p
        lgeos.GEOSPrepare.argtypes = [c_void_p]

        lgeos.GEOSPreparedGeom_destroy.restype = None
        lgeos.GEOSPreparedGeom_destroy.argtypes = [c_void_p]

        lgeos.GEOSPreparedIntersects.restype = c_int
        lgeos.GEOSPreparedIntersects.argtypes = [c_void_p, c_void_p]

        lgeos.GEOSPreparedContains.restype = c_int
        lgeos.GEOSPreparedContains.argtypes = [c_void_p, c_void_p]

        lgeos.GEOSPreparedContainsProperly.restype = c_int
        lgeos.GEOSPreparedContainsProperly.argtypes = [c_void_p, c_void_p]

        lgeos.GEOSPreparedCovers.restype = c_int
        lgeos.GEOSPreparedCovers.argtypes = [c_void_p, c_void_p]

        lgeos.GEOSisValidReason.restype = allocated_c_char_p
        lgeos.GEOSisValidReason.argtypes = [c_void_p]

    # Other, GEOS C API 1.5.0+
    if geosVersion >= (1, 5, 0):
        lgeos.GEOSUnionCascaded.restype = c_void_p
        lgeos.GEOSUnionCascaded.argtypes = [c_void_p]

    # 1.6.0
    if geosVersion >= (1, 6, 0):
        # Linear referencing features aren't found in versions 1.5,
        # but not in all libs versioned 1.6.0 either!
        if hasattr(lgeos, 'GEOSProject'):
            lgeos.GEOSSingleSidedBuffer.restype = c_void_p
            lgeos.GEOSSingleSidedBuffer.argtypes = [c_void_p, c_double, c_int, c_int, c_double, c_int]

            lgeos.GEOSProject.restype = c_double
            lgeos.GEOSProject.argtypes = [c_void_p, c_void_p]

            lgeos.GEOSProjectNormalized.restype = c_double
            lgeos.GEOSProjectNormalized.argtypes = [c_void_p, c_void_p]

            lgeos.GEOSInterpolate.restype = c_void_p
            lgeos.GEOSInterpolate.argtypes = [c_void_p, c_double]

            lgeos.GEOSInterpolateNormalized.restype = c_void_p
            lgeos.GEOSInterpolateNormalized.argtypes = [c_void_p, c_double]

    # TODO: Find out what version of geos_c came with geos 3.3.0
    if geosVersion >= (1, 6, 3):
        lgeos.GEOSUnaryUnion.restype = c_void_p
        lgeos.GEOSUnaryUnion.argtypes = [c_void_p]
