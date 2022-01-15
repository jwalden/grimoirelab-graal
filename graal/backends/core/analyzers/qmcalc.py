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
import pandas as pd
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
            raise GraalError(cause="Error on reading cqmetrics metric names from %" % metrics_names_path)
            
        self.metrics_names = name_string.split("\t")

    def __is_metric_int(self, metric):
        metric[0] == 'n' or metric.endswith("_length_min") or metric.endswith("_length_max") or metric.endswith("_nesting_min") or metric.endswith("_nesting_max")

    def __analyze_file(self, message, file_path):
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

        results['path'] = file_path
        results['ext'] = GraalRepository.extension(file_path)

        return results

    def __analyze_repository(self, message, file_paths):
        """Add information LOC, total files, blank and commented lines using CLOC for the entire repository

        :param message: message from standard output after execution of qmcalc

        :returns result: dict of the results of the analysis over a repository
        """

        # Construct data frame with metrics as columns, files as rows
        results = []
        i = 0
        for line in message.strip().split("\n"):
            print(file_paths[i])
            value_strings = line.rstrip().split("\t")
            file_results = dict(zip(self.metrics_names, value_strings))
            for metric in file_results:
                if len(file_results[metric]) == 0:
                    file_results[metric] = '0'
            i = i + 1

        metrics_df = pd.DataFrame(data = results)
        # metrics_df = metrics_df.convert_dtypes()
        for col in metrics_df.columns:
            if self.__is_metric_int(col):
                metrics_df[col] = pd.to_numeric(metrics_df[col], errors='coerce').astype('Int64') 
            else:
                metrics_df[col] = pd.to_numeric(metrics_df[col], errors='coerce')

        print(metrics_df.dtypes)
        print('exit here')
        exit(1)
        metrics_df.to_csv('metrics.csv', index=False)
        nfiles = len(metrics_df)

        # Groups of columns that need to be summarized in non-sum() ways
        mincols = [col for col in metrics_df.columns if col.endswith('min')]
        maxcols = [col for col in metrics_df.columns if col.endswith('max')]
        meancols = [col for col in metrics_df.columns if col.endswith('mean')]
        sdcols = [col for col in metrics_df.columns if col.endswith('sd')]
        mediancols = [col for col in metrics_df.columns if col.endswith('median')]

        # Summarize each column based on metric type, sum() by default
        sums = [ nfiles ]
        for col in metrics_df.columns:
            print(col)
            print(col.dtype)
            if col in mincols:
                res = metrics_df[col].min()
            elif col in maxcols:
                res = metrics_df[col].max()
            elif col in meancols:
                res = metrics_df[col].mean()
            elif col in mediancols:
                res = metrics_df[col].median()
            elif col in sdcols:
                mean_col = col.replace('sd', 'mean')
                res = metrics_df[mean_col].std()
            else:
                res = metrics_df[col].sum()
            sums.append(res)

        # Build results dictionary with extra 'nfiles' metric
        metrics_names = [ 'nfiles' ] + self.metrics_names
        results = dict(zip(metrics_names, sums))

        return results

    def analyze(self, **kwargs):
        """Add information using qmcalc

        :param file_path: path of a single C source or header file to analyze
        :param repository_level: set to True if analysis has to be performed on a repository

        :returns result: dict of the results of the analysis
        """

        file_path = kwargs['file_path']
        repository_level = kwargs.get('repository_level', False)

        if repository_level:
            file_paths = list(Path(file_path).glob('**/*.[ch]'))
        else:
            file_paths = [file_path]

        try:
            qmcalc_command = ['qmcalc'] + file_paths
            # print(qmcalc_command) #FIXME: debug print
            message = subprocess.check_output(qmcalc_command).decode("utf-8")
        except subprocess.CalledProcessError as e:
            raise GraalError(cause="QMCalc failed at %s, %s" % (file_path, e.output.decode("utf-8")))
        finally:
            subprocess._cleanup()

        if repository_level:
            results = self.__analyze_repository(message, file_paths)
        else:
            results = self.__analyze_file(message, file_path)

        print(results) # FIXME: debug print
        exit(1)
        return results
