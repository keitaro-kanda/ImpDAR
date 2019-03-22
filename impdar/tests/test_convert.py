#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2019 dlilien <dlilien@berens>
#
# Distributed under terms of the MIT license.

"""

"""
import os
import unittest
import numpy as np
from impdar.lib import convert
from impdar.lib._RadarDataSaving import conversions_enabled

THIS_DIR = os.path.dirname(os.path.abspath(__file__))


class TestConvert(unittest.TestCase):

    @unittest.skipIf(not conversions_enabled, 'No GDAL on this version')
    def test_guessload2shp(self):
        convert.convert(os.path.join(THIS_DIR, 'input_data', 'small_data.mat'), 'shp')
        self.assertTrue(os.path.exists(os.path.join(THIS_DIR, 'input_data', 'small_data.shp')))

        convert.convert([os.path.join(THIS_DIR, 'input_data', 'test_pe.DT1')], 'shp')
        self.assertTrue(os.path.exists(os.path.join(THIS_DIR, 'input_data', 'test_pe.shp')))

        convert.convert([os.path.join(THIS_DIR, 'input_data', 'test_gssi.DZT')], 'shp')
        self.assertTrue(os.path.exists(os.path.join(THIS_DIR, 'input_data', 'test_gssi.shp')))

    @unittest.skipIf(not conversions_enabled, 'No GDAL on this version')
    def test_knownload2shp(self):
        convert.convert(os.path.join(THIS_DIR, 'input_data', 'small_data.mat'), 'shp', in_fmt='mat')
        self.assertTrue(os.path.exists(os.path.join(THIS_DIR, 'input_data', 'small_data.shp')))

        convert.convert([os.path.join(THIS_DIR, 'input_data', 'test_pe.DT1')], 'shp', in_fmt='pe')
        self.assertTrue(os.path.exists(os.path.join(THIS_DIR, 'input_data', 'test_pe.shp')))

        convert.convert([os.path.join(THIS_DIR, 'input_data', 'test_gssi.DZT')], 'shp', in_fmt='gssi')
        self.assertTrue(os.path.exists(os.path.join(THIS_DIR, 'input_data', 'test_gssi.shp')))

    @unittest.skipIf(not conversions_enabled, 'No GDAL on this version')
    def test_knownload2mat(self):
        convert.convert([os.path.join(THIS_DIR, 'input_data', 'test_pe.DT1')], 'mat', in_fmt='pe')
        self.assertTrue(os.path.exists(os.path.join(THIS_DIR, 'input_data', 'test_pe.mat')))

        convert.convert([os.path.join(THIS_DIR, 'input_data', 'test_gssi.DZT')], 'mat', in_fmt='gssi')
        self.assertTrue(os.path.exists(os.path.join(THIS_DIR, 'input_data', 'test_gssi.mat')))

    def test_badinsout(self):
        with self.assertRaises(ValueError):
            convert.convert([os.path.join(THIS_DIR, 'input_data', 'small_data.mat')], 'dummy')
        with self.assertRaises(ValueError):
            convert.convert([os.path.join(THIS_DIR, 'input_data', 'small_data.wtf')], 'shp')

    def tearDown(self):
        for ext in ['shp', 'shx', 'dbf', 'prj']:
            for pref in ['small_data', 'test_gssi', 'test_pe']:
                if os.path.exists(os.path.join(THIS_DIR, 'input_data', pref + '.' + ext)):
                    os.remove(os.path.join(THIS_DIR, 'input_data', pref + '.' + ext))
        for pref in ['test_gssi', 'test_pe']:
            if os.path.exists(os.path.join(THIS_DIR, 'input_data', pref + '.mat')):
                os.remove(os.path.join(THIS_DIR, 'input_data', pref + '.mat'))


if __name__ == '__main__':
    unittest.main()