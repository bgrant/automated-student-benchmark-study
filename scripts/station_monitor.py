#! /usr/bin/env python

"""
Run simple_grading.sh on a few stations, display output as a formatted table.

:author: Robert Grant <robert.david.grant@utexas.edu>

:copyright:
    Copyright 2011 The University of Texas at Austin

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""
__docformat__ = "restructuredtext en"


import argparse
import os 
import string
import time
import json

from subprocess import Popen
from subprocess import PIPE
from subprocess import call

STATION_PATH = '/media/asb_share/stations'


def run_simple_grading(stations=['1','2','3','4','5','6']):
    """
    Run simple_grading.sh over the list of given station numbers.

    See command line option documentation for parameter documentation.
    """

    station_objects = []
    for num in stations:
        station_json = Popen(["./simple_grading.sh",
            os.path.join(STATION_PATH, "station_" + num)],
            stdout=PIPE).communicate()[0]
        station_json = station_json.replace('\n','')
        stats = json.loads(station_json)
        stats['Station'] = num
        station_objects.append(stats)
    return station_objects


def format_table(station_objects):
    """
    Returns station stats as a formatted table.

    :param station_objects: list returned from simple_grading.sh
    """
    def format_row(key):
        """Format and return a single row of the table"""
        row = [key.rjust(12)] + \
            [station[key].rjust(15) for station in station_objects]
        return string.join(row)

    header = ["Station Monitor:", ""]
    row_titles = ["Station", "Pre-Test"] + \
        ["Quiz " + x for x in ["1_1", "2_3", "2_6", "3-4_3", "3-4_6"]] + \
        ["Post-Test-1", "Post-Test-2", "Final-Test"]
    footer = ["", "(Ctrl-C to exit)"]

    table = header + [format_row(r) for r in row_titles] + footer
    table = string.join(table, "\n")

    return table


def clear_screen():
    """
    Clear screen; really should be using curses or something
    """
    try:
        retcode = call("clear", shell=True)
        if retcode < 0:
            print >>sys.stderr, "Child was terminated by signal", -retcode
    except OSError, e:
        print >>sys.stderr, "Clear failed:", e


def run(station_list, poll_interval=5):
    """
    Monitor stations in `station_list`, refreshing at an interval of
    `poll_interval`.
    """
    buf = run_simple_grading(station_list)
    while True:
        clear_screen()
        print format_table(buf)
        buf = run_simple_grading(station_list)
        time.sleep(poll_interval)


def main():
    """Command line interface"""

    # create the parser
    parser = argparse.ArgumentParser(
        description='Generate a study for a subject given their treatment.')

    # add the arguments
    parser.add_argument(
        'stations', nargs='*', choices=[[],'1','2','3','4','5','6'],
        help='the station numbers to be graded (default all)')
    parser.add_argument(
        '-i', '--poll-interval', type=int, default=5,
        help='the poll interval in seconds (default=5)')

    # parse the command line
    args = parser.parse_args()

    if args.stations == []:
        args.stations = ['1','2','3','4','5','6']

    try:
        run(args.stations, args.poll_interval)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
