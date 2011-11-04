#! /usr/bin/env python

"""
Simple script to distribute files after they've been generated.

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
import shutil
import os
import subprocess


STATION_PATH = "/media/asb_share/stations"


def distribute(src_path, station_number):
    """
    Does the work of distribution.

    See the command line interface comments for details.
    """

    dist_path = STATION_PATH + "/station_" + station_number + "/lib"

    print "Removing %s..." % dist_path
    if os.path.exists(dist_path):
        shutil.rmtree(dist_path)

    print "Copying %s to %s..." % (src_path, dist_path)
    # shutil copytree had errors os I have to call out to cp
#    shutil.copytree(src_path, dist_path)
    retval = subprocess.check_call(["cp", "-R", src_path, dist_path])

    print "Done."


def main():
    """Command line interface"""

    # create the parser
    parser = argparse.ArgumentParser(
        description="""Simple script to distribute files after they've been
        generated.  BE SURE YOU HAVE BACKED UP THE TARGET STATION'S DATA FIRST,
        AS IT WILL BE DELETED.""")

    # add the arguments
    parser.add_argument('src_path', 
        help='The folder to distrbute (probably ASB_Study).')
    parser.add_argument('station_number', 
        help='The station number, for example the "5" in "station_5".')

    # parse the command line
    args = parser.parse_args()

    distribute(args.src_path, args.station_number)


if __name__ == '__main__':
    main()
