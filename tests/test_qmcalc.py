#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2020 Bitergia
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# Authors:
#     James Walden <james.walden@acm.org>
#     Valerio Cosentino <valcos@bitergia.com>
#     inishchith <inishchith@gmail.com>
#

import os
import subprocess
import unittest.mock

from base_analyzer import (TestCaseAnalyzer,
                           ANALYZER_TEST_C_FILE)

from graal.backends.core.analyzers.qmcalc import QMCalc
from graal.graal import GraalError


class TestQMCalc(TestCaseAnalyzer):
    """QMCalc tests"""

    def test_initialization(self):
        """Test whether attributes are initializated"""

        qmc = QMCalc()
        self.assertEqual(len(qmc.metrics_names), 111)

    def test_analyze_fields_present(self):
        """Test whether qmcalc returns the expected fields """

        qmc = QMCalc()
        # kwargs = {'file_path': 'data/sample_code.c'} FIXME
        kwargs = {'file_path': os.path.join(self.tmp_data_path, ANALYZER_TEST_C_FILE)}
        result = qmc.analyze(**kwargs)

        for metric_name in qmc.metrics_names:
            self.assertIn(metric_name, result)

    def test_analyze_c(self):
        """Test whether qmcalc returns expected code metric values"""

        qmc = QMCalc()
        kwargs = {'file_path': os.path.join(self.tmp_data_path, ANALYZER_TEST_C_FILE)}
        result = qmc.analyze(**kwargs)

        self.assertEqual(result['nchar'], 839)
        self.assertEqual(result['nline'], 44)
        self.assertEqual(result['nfunction'], 3)
        self.assertEqual(result['nfunction2'], 3)
        self.assertEqual(result['identifier_length_max'], 14)
        self.assertEqual(result['identifier_length_min'], 1)
        self.assertEqual(result['line_length_min'], 0)
        self.assertEqual(result['line_length_median'], 15.5)
        self.assertEqual(result['line_length_max'], 73)
        self.assertEqual(result['ncpp_directive'], 5)
        self.assertEqual(result['ncpp_conditional'], 1)
        self.assertEqual(result['ncpp_include'], 2)
        self.assertEqual(result['ncomment'], 1)
        self.assertEqual(result['nconst'], 1)
        self.assertEqual(result['nenum'], 0)
        self.assertEqual(result['ngoto'], 0)
        self.assertEqual(result['nsigned'], 0)
        self.assertEqual(result['nstruct'], 0)
        self.assertEqual(result['nunion'], 0)
        self.assertEqual(result['nunsigned'], 1)
        self.assertEqual(result['nvoid'], 2)
        self.assertEqual(result['halstead_mean'], 124.599)
        self.assertEqual(result['halstead_median'], 114.714)
        self.assertEqual(result['halstead_max'], 228.898)
        self.assertEqual(result['halstead_min'], 30.1851)
        self.assertEqual(result['statement_nesting_max'], 2)

#     def test_analyze_repository_level(self):
#         """Test whether qmcalc returns the expected fields data for repository level"""

#         qmc = QMCalc()
#         kwargs = {
#             'file_path': self.origin_path,
#             'repository_level': True
#         }
#         results = qmc.analyze(**kwargs)
#         result = results[next(iter(results))]

#         self.assertIn('blanks', result)
#         self.assertTrue(type(result['blanks']), int)
#         self.assertIn('comments', result)
#         self.assertTrue(type(result['comments']), int)
#         self.assertIn('loc', result)
#         self.assertTrue(type(result['loc']), int)
#         self.assertIn('total_files', result)
#         self.assertTrue(type(result['total_files']), int)

#     @unittest.mock.patch('subprocess.check_output')
#     def test_analyze_error(self, check_output_mock):
#         """Test whether an exception is thrown in case of errors"""

#         check_output_mock.side_effect = subprocess.CalledProcessError(-1, "command", output=b'output')

#         qmc = QMCalc()
#         kwargs = {'file_path': os.path.join(self.tmp_data_path, ANALYZER_TEST_FILE)}
#         with self.assertRaises(GraalError):
#             _ = qmc.analyze(**kwargs)


if __name__ == "__main__":
    unittest.main()
