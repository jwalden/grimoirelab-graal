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

import subprocess
from pathlib import Path

from graal.graal import (GraalError,
                         GraalRepository)
from .analyzer import Analyzer


class QMCalc(Analyzer):
    """A wrapper for QMCalc (cqmetrics)

    This class allows to call QMCalc with a file, parses
    the result of the analysis and returns it as a dict.

    :param diff_timeout: max time to compute diffs of a given file
    """
    version = '0.0.1'
    metrics_names_file = 'cqmetrics-names.tsv'
    metrics_names_path = Path(__file__).parent.absolute().joinpath(metrics_names_file)

    def __init__(self):
        try:
            with open(QMCalc.metrics_names_path) as f:
                name_string = f.read().rstrip()
        except:
            raise GraalError(cause="Error on reading cqmetrics names from %" % metrics_names_path)
            
        self.metrics_names = name_string.split("\t")

    def __is_metric_int(self, metric):
        metric[0] == 'n' or metric.endswith("_length_min") or metric.endswith("_length_max") or metric.endswith("_nesting_min") or metric.endswith("_nesting_max")

    def __analyze_file(self, message):
        """Convert tab-separated metrics values from qmcalc into a dictionary

        :param message: message from standard output after execution of qmcalc

        :returns result: dict of the results of qmcalc analysis of a file
        """

        value_strings = message.rstrip().split("\t")
        results = dict(zip(self.metrics_names, value_strings))
        for metric in results:
            if self.__is_metric_int(metric):
                results[metric] = int(results[metric])
            else:
                results[metric] = float(results[metric])

        return results

    def __analyze_repository(self, message):
        # FIXME: not implemented yet
        """Add information LOC, total files, blank and commented lines using CLOC for the entire repository

        :param message: message from standard output after execution of qmcalc

        :returns result: dict of the results of the analysis over a repository
        """

        results = {}
        flag = False

        for line in message.strip().split("\n"):
            if flag:
                if line.lower().startswith("sum"):
                    break
                elif not line.startswith("-----"):
                    digested_split = line.split()
                    langauge, files_info = digested_split[:-4], digested_split[-4:]
                    language = " ".join(langauge)
                    total_files, blank_lines, commented_lines, loc = map(int, files_info)
                    language_result = {
                        "total_files": total_files,
                        "blanks": blank_lines,
                        "comments": commented_lines,
                        "loc": loc
                    }
                    results[language] = language_result

            if line.lower().startswith("language"):
                flag = True

        return results

    def analyze(self, **kwargs):
        """Add information using qmcalc

        :param file_path: file path
        :param repository_level: set to True if analysis has to be performed on a repository

        :returns result: dict of the results of the analysis
        """

        file_path = kwargs['file_path']
        repository_level = kwargs.get('repository_level', False)
        # FIXME: we currently only handle the single file case

        try:
            qmcalc_command = ['qmcalc', file_path]
            message = subprocess.check_output(qmcalc_command).decode("utf-8")
        except subprocess.CalledProcessError as e:
            raise GraalError(cause="QMCalc failed at %s, %s" % (file_path, e.output.decode("utf-8")))
        finally:
            subprocess._cleanup()

        if repository_level:
            results = self.__analyze_repository(message)
        else:
            results = self.__analyze_file(message)
            results['ext'] = GraalRepository.extension(file_path)

        print(results) # FIXME: debug print
        return results
