#! /usr/bin/env python

"""
Simple script to back up subject workstation data.

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
from os.path import join as osjoin
#import shutil
import subprocess

BASE_PATH = osjoin('/', 'media', 'asb_share')
DEFAULT_STATION_PATH = osjoin(BASE_PATH, 'stations')
DEFAULT_BACKUP_PATH = osjoin(BASE_PATH, 'data')


def backup(src_path, run_path, backup_path):
    print "Backing up %s to %s" % (src_path, backup_path)
    if not os.path.isdir(backup_path):
        # shutil.copytree had errors os I have to call out to cp
        # shutil.copytree(src_path, dist_path)
        retval = subprocess.check_call(["mkdir", "-p", run_path])
        retval = subprocess.check_call(["cp", "-R", src_path, backup_path])
    else:
        print "Directory %s exists, skipping..." % backup_path


def backup_all(run_number, stations):
    """
    Backup all indicated stations.

    See `main` for detailed parameter documentation.
    """
    run = 'Run' + run_number
    for s in stations:
        station = 'station_' + s
        src_path = osjoin(DEFAULT_STATION_PATH, station)
        run_path = osjoin(DEFAULT_BACKUP_PATH, run)
        backup_path = osjoin(run_path, station)
        backup(src_path, run_path, backup_path)

def main():
    """Command line interface"""

    # create the parser
    parser = argparse.ArgumentParser(
        description="Simple script to backup subject workstation data.")

    # add the arguments
    parser.add_argument(
        'run_number', help='the number assigned to this run, e.g., 5')
    parser.add_argument(
        '-s', '--stations', nargs='+', choices=['1','2','3','4','5','6'],
        default=['1','2','3','4','5','6'],
        help='the station numbers to be backed up')

    # parse the command line
    args = parser.parse_args()

    backup_all(args.run_number, args.stations)


if __name__ == '__main__':
    main()
