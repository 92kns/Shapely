import unittest
from math import pi
from shapely.algorithms import transform
from shapely.wkt import loads as load_wkt
from shapely.geometry import Point

class AffineTestCase(unittest.TestCase):

    def test_affine_params(self):
        g = load_wkt('LINESTRING(2.4 4.1, 2.4 3, 3 3)')
        self.assertRaises(TypeError, transform.affine, g, None)
        self.assertRaises(TypeError, transform.affine, g, '123456')
        self.assertRaises(ValueError, transform.affine, g, [1,2,3,4,5,6,7,8,9])
        self.assertRaises(AttributeError, transform.affine, None, [1,2,3,4,5,6])

    def test_affine_geom_types(self):
        matrix2d = (1, 0,
                    0, 1,
                    0, 0)
        matrix3d = (1, 0, 0,
                    0, 1, 0,
                    0, 0, 1,
                    0, 0, 0)
        def test_geom(g2, g3=None):
            self.assertFalse(g2.has_z)
            a2 = transform.affine(g2, matrix2d)
            self.assertFalse(a2.has_z)
            self.assertTrue(g2.equals(a2))
            if g3 is not None:
                self.assertTrue(g3.has_z)
                a3 = transform.affine(g3, matrix3d)
                self.assertTrue(a3.has_z)
                self.assertTrue(g3.equals(a3))
            return
        pt2d = load_wkt('POINT(12.3 45.6)')
        pt3d = load_wkt('POINT(12.3 45.6 7.89)')
        test_geom(pt2d, pt3d)
        ls2d = load_wkt('LINESTRING(0.9 3.4, 0.7 2, 2.5 2.7)')
        ls3d = load_wkt('LINESTRING(0.9 3.4 3.3, 0.7 2 2.3, 2.5 2.7 5.5)')
        test_geom(ls2d, ls3d)
        test_geom(load_wkt('POLYGON((0.9 2.3, 0.5 1.1, 2.4 0.8, 0.9 2.3), '\
                           '(1.1 1.7, 0.9 1.3, 1.4 1.2, 1.1 1.7), '\
                           '(1.6 1.3, 1.7 1, 1.9 1.1, 1.6 1.3))'))
        test_geom(load_wkt('MULTIPOINT ((-300 300), (700 300), '\
                           '(-800 -1100), (200 -300))'))
        test_geom(load_wkt('MULTILINESTRING((0 0, -0.7 -0.7, 0.6 -1), '\
                           '(-0.5 0.5, 0.7 0.6, 0 -0.6))'))
        test_geom(load_wkt('MULTIPOLYGON(((900 4300, -1100 -400, '\
                           '900 -800, 900 4300)), '\
                           '((1200 4300, 2300 4400, 1900 1000, 1200 4300)))'))
        # GeometryCollection fails, since it does not have a good constructor
        gc = load_wkt('GEOMETRYCOLLECTION(POINT(20 70),'\
                      ' POLYGON((60 70, 13 35, 60 -30, 60 70)),'\
                      ' LINESTRING(60 70, 50 100, 80 100))')
        self.assertRaises(TypeError, test_geom, gc) # TODO: fix this

    def test_affine_2d(self):
        g = load_wkt('LINESTRING(2.4 4.1, 2.4 3, 3 3)')
        # custom scale and translate
        expected2d = load_wkt('LINESTRING(-0.2 14.35, -0.2 11.6, 1 11.6)')
        matrix2d = (2, 0,
                    0, 2.5,
                    -5, 4.1)
        a2 = transform.affine(g, matrix2d)
        self.assertTrue(a2.almost_equals(expected2d))
        self.assertFalse(a2.has_z)
        # Make sure a 3D matrix does not make a 3D shape from a 2D input
        matrix3d = (2, 0, 0,
                    0, 2.5, 0,
                    0, 0, 10,
                    -5, 4.1, 100)
        a3 = transform.affine(g, matrix3d)
        self.assertTrue(a3.almost_equals(expected2d))
        self.assertFalse(a3.has_z)

    def test_affine_3d(self):
        g2 = load_wkt('LINESTRING(2.4 4.1, 2.4 3, 3 3)')
        g3 = load_wkt('LINESTRING(2.4 4.1 100.2, 2.4 3 132.8, 3 3 128.6)')
        # custom scale and translate
        matrix2d = (2, 0,
                    0, 2.5,
                    -5, 4.1)
        matrix3d = (2, 0, 0,
                    0, 2.5, 0,
                    0, 0, 0.3048,
                    -5, 4.1, 100)
        # Combinations of 2D and 3D geometries and matrices
        a22 = transform.affine(g2, matrix2d)
        a23 = transform.affine(g2, matrix3d)
        a32 = transform.affine(g3, matrix2d)
        a33 = transform.affine(g3, matrix3d)
        # Check dimensions
        self.assertFalse(a22.has_z)
        self.assertFalse(a23.has_z)
        self.assertTrue(a32.has_z)
        self.assertTrue(a33.has_z)
        # 2D equality checks
        expected2d = load_wkt('LINESTRING(-0.2 14.35, -0.2 11.6, 1 11.6)')
        expected3d = load_wkt('LINESTRING(-0.2 14.35 130.54096, '\
                              '-0.2 11.6 140.47744, 1 11.6 139.19728)')
        expected32 = load_wkt('LINESTRING(-0.2 14.35 100.2, '\
                              '-0.2 11.6 132.8, 1 11.6 128.6)')
        self.assertTrue(a22.almost_equals(expected2d))
        self.assertTrue(a23.almost_equals(expected2d))
        # Do explicit 3D check of coordinate values
        for a, e in zip(a32.coords, expected32.coords):
            for ap, ep in zip(a, e):
                self.assertAlmostEqual(ap, ep)
        for a, e in zip(a33.coords, expected3d.coords):
            for ap, ep in zip(a, e):
                self.assertAlmostEqual(ap, ep)

class TransformOpsTestCase(unittest.TestCase):

    def test_rotate(self):
        ls = load_wkt('LINESTRING(240 400, 240 300, 300 300)')
        # counter-clockwise degrees
        rls = transform.rotate(ls, 90)
        els = load_wkt('LINESTRING(220 320, 320 320, 320 380)')
        self.assertTrue(rls.equals(els))
        # retest with named parameters for the same result
        rls = transform.rotate(geom=ls, angle=90, origin='center')
        self.assertTrue(rls.equals(els))
        # clockwise radians
        rls = transform.rotate(ls, -pi/2, use_radians=True)
        els = load_wkt('LINESTRING(320 380, 220 380, 220 320)')
        self.assertTrue(rls.equals(els))
        ## other `origin` parameters
        # around the centroid
        rls = transform.rotate(ls, 90, origin='centroid')
        els = load_wkt('LINESTRING(182.5 320, 282.5 320, 282.5 380)')
        self.assertTrue(rls.equals(els))
        # around the second coordinate tuple
        rls = transform.rotate(ls, 90, origin=ls.coords[1])
        els = load_wkt('LINESTRING(140 300, 240 300, 240 360)')
        self.assertTrue(rls.equals(els))
        # around the absolute Point of origin
        rls = transform.rotate(ls, 90, origin=Point(0,0))
        els = load_wkt('LINESTRING(-400 240, -300 240, -300 300)')
        self.assertTrue(rls.equals(els))

    def test_scale(self):
        ls = load_wkt('LINESTRING(240 400 10, 240 300 30, 300 300 20)')
        # test defaults of 1.0
        sls = transform.scale(ls)
        self.assertTrue(sls.equals(ls))
        # different scaling in different dimensions
        sls = transform.scale(ls, 2, 3, 0.5)
        els = load_wkt('LINESTRING(210 500 5, 210 200 15, 330 200 10)')
        self.assertTrue(sls.equals(els))
        # Do explicit 3D check of coordinate values
        for a, b in zip(sls.coords, els.coords):
            for ap, bp in zip(a, b):
                self.assertEqual(ap, bp)
        # retest with named parameters for the same result
        sls = transform.scale(geom=ls, xfact=2, yfact=3, zfact=0.5,
                              origin='center')
        self.assertTrue(sls.equals(els))
        ## other `origin` parameters
        # around the centroid
        sls = transform.scale(ls, 2, 3, 0.5, origin='centroid')
        els = load_wkt('LINESTRING(228.75 537.5, 228.75 237.5, 348.75 237.5)')
        self.assertTrue(sls.equals(els))
        # around the second coordinate tuple
        sls = transform.scale(ls, 2, 3, 0.5, origin=ls.coords[1])
        els = load_wkt('LINESTRING(240 600, 240 300, 360 300)')
        self.assertTrue(sls.equals(els))
        # around some other 3D Point of origin
        sls = transform.scale(ls, 2, 3, 0.5, origin=Point(100, 200, 1000))
        els = load_wkt('LINESTRING(380 800 505, 380 500 515, 500 500 510)')
        self.assertTrue(sls.equals(els))
        # Do explicit 3D check of coordinate values
        for a, b in zip(sls.coords, els.coords):
            for ap, bp in zip(a, b):
                self.assertEqual(ap, bp)

    def test_skew(self):
        ls = load_wkt('LINESTRING(240 400 10, 240 300 30, 300 300 20)')
        # test default shear angles of 0.0
        sls = transform.skew(ls)
        self.assertTrue(sls.equals(ls))
        # different shearing in x- and y-directions
        sls = transform.skew(ls, 15, -30)
        els = load_wkt('LINESTRING (253.39745962155615 417.3205080756888, '\
                       '226.60254037844385 317.3205080756888, '\
                       '286.60254037844385 282.67949192431126)')
        self.assertTrue(sls.almost_equals(els))
        # retest with radians for the same result
        sls = transform.skew(ls, pi/12, -pi/6, use_radians=True)
        self.assertTrue(sls.almost_equals(els))
        # retest with named parameters for the same result
        sls = transform.skew(geom=ls, xs=15, ys=-30,
                             origin='center', use_radians=False)
        self.assertTrue(sls.almost_equals(els))
        ## other `origin` parameters
        # around the centroid
        sls = transform.skew(ls, 15, -30, origin='centroid')
        els = load_wkt('LINESTRING(258.42150697963973 406.49519052838332, '\
                       '231.6265877365273980 306.4951905283833185, '\
                       '291.6265877365274264 271.8541743770057337)')
        self.assertTrue(sls.almost_equals(els))
        # around the second coordinate tuple
        sls = transform.skew(ls, 15, -30, origin=ls.coords[1])
        els = load_wkt('LINESTRING(266.7949192431123038 400, 240 300, '\
                       '300 265.3589838486224153)')
        self.assertTrue(sls.almost_equals(els))
        # around the absolute Point of origin
        sls = transform.skew(ls, 15, -30, origin=Point(0,0))
        els = load_wkt('LINESTRING(347.179676972449101 261.435935394489832, '\
                       '320.3847577293367976 161.4359353944898317, '\
                       '380.3847577293367976 126.7949192431122754)')
        self.assertTrue(sls.almost_equals(els))

    def test_translate(self):
        ls = load_wkt('LINESTRING(240 400 10, 240 300 30, 300 300 20)')
        # test default offset of 0.0
        tls = transform.translate(ls)
        self.assertTrue(tls.equals(ls))
        # test all offsets
        tls = transform.translate(ls, 100, 400, -10)
        els = load_wkt('LINESTRING(340 800 0, 340 700 20, 400 700 10)')
        self.assertTrue(tls.equals(els))
        # Do explicit 3D check of coordinate values
        for a, b in zip(tls.coords, els.coords):
            for ap, bp in zip(a, b):
                self.assertEqual(ap, bp)
        # retest with named parameters for the same result
        tls = transform.translate(geom=ls, xoff=100, yoff=400, zoff=-10)
        self.assertTrue(tls.equals(els))

    def test_scalerotatetranslate(self):
        ls = load_wkt('LINESTRING(240 400 10, 240 300 30, 300 300 20)')
        # test defaults
        tls = transform.translate(ls)
        self.assertTrue(tls.equals(ls))
        # test all three
        tls = transform.scalerotatetranslate(ls, 2, 3, 0.5, 30,
                                             100, 400, -10)
        els = load_wkt('LINESTRING(243.03847577293368 849.9038105676659 -5, '\
                       '393.0384757729336200 590.0961894323343100 5, '\
                       '496.9615242270662600 650.0961894323343100 0)')
        self.assertTrue(tls.almost_equals(els))
        # Do explicit 3D check of coordinate values
        for a, b in zip(tls.coords, els.coords):
            for ap, bp in zip(a, b):
                self.assertEqual(ap, bp)
        # recheck with named parameters
        tls = transform.scalerotatetranslate(geom=ls, xfact=2, yfact=3,
                                             zfact=0.5, angle=30,
                                             xoff=100, yoff=400, zoff=-10,
                                             origin='center', use_radians=False)
        self.assertTrue(tls.almost_equals(els))
        # test scale and rotate in radians
        tls = transform.scalerotatetranslate(ls, 2, 3, 0.5, pi/6,
                                             use_radians=True)
        els = load_wkt('LINESTRING(143.03847577293368 449.90381056766591, '\
                       '293.0384757729336200 190.0961894323343100, '\
                       '396.9615242270662600 250.0961894323343100)')
        self.assertTrue(tls.almost_equals(els))
        # test offsets only
        tls = transform.scalerotatetranslate(ls, xoff=100, yoff=400, zoff=-10)
        els = load_wkt('LINESTRING(340 800, 340 700, 400 700)')
        self.assertTrue(tls.almost_equals(els))
        # Do explicit 3D check of coordinate values
        for a, b in zip(tls.coords, els.coords):
            for ap, bp in zip(a, b):
                self.assertEqual(ap, bp)

def test_suite():
    loader = unittest.TestLoader()
    return unittest.TestSuite([
        unittest.TestLoader().loadTestsFromTestCase(AffineTestCase),
        unittest.TestLoader().loadTestsFromTestCase(TransformOpsTestCase)])
