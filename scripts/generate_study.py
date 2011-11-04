#! /usr/bin/env python

"""
Top level script to generate a set of files for a subject in the Automated
Student Benchmark study.

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
import shutil
import sim_config
import nav_pages
import metadata


def make_distribution(nims, src_path, dist_path='ASB_Study',
        no_quiz_feedback='False', test_time=300):
    """
    Generate a set of study files based on given options

    See command line option documentation for parameter documentation.
    """
    cwd = os.getcwd()

    # Copy unchanged directories to dist_path
    patterns = ('*.ppt', '*.doc', '.DS_Store', '.svn', '.git')
    os.mkdir(dist_path)
    shutil.copytree(os.path.join(src_path, 'curriculum'),
            os.path.join(dist_path, 'curriculum'),
            ignore=shutil.ignore_patterns(*patterns))
    shutil.copytree(os.path.join(src_path, 'reference'),
            os.path.join(dist_path, 'reference'),
            ignore=shutil.ignore_patterns(*patterns))
    shutil.copytree(os.path.join(src_path, 'quizzes'), 
            os.path.join(dist_path, 'quizzes'),
            ignore=shutil.ignore_patterns(*patterns))

    # Create simulator directories in dist_path
    for config in ['pretest', 'feedback', 'realtime', 'test', 'penultimate',
            'final']:
        simdir = os.path.join(dist_path, config + '_simulator')
        shutil.copytree(os.path.join(src_path, 'simulator'), simdir,
            ignore=shutil.ignore_patterns(*patterns))
        os.chdir(simdir)
        sim_config.write(config, test_time)
        os.chdir(cwd)

    # Log study metadata in dist_path
    metadata.write(dist_path, nims, no_quiz_feedback, test_time)

    os.chdir(dist_path)
    # Create navigation page in dist_path
    nav_pages.write(nims, 'ASB_Study.htm', no_quiz_feedback, test_time)
    os.chdir(cwd)


def main():
    """Command line interface"""

    # create the parser
    parser = argparse.ArgumentParser(
        description='Generate a study for a subject given their treatment.')

    # add the arguments
    parser.add_argument(
        'nims', nargs='+', choices=['t','e','f'], 
        help='the NIMs to be used in this treatment.')
    parser.add_argument('-n', '--no-quiz-feedback', action='store_true', 
            help="don't tell subjects their quiz scores (default: False)")
    parser.add_argument('-t', '--test-time', type=int, default=300,
            help="time for a single test scenario, in seconds (default: 300)")
    parser.add_argument('-s', '--src-path', default=os.path.join('..',
        'student-materials'), help='path to directory containing study source (default: ../student_materials)')
    parser.add_argument('-d', '--dist-path', default='ASB_Study',
            help='name of directory to create for distribution (default: ASB_Study)')

    # parse the command line
    args = parser.parse_args()

    make_distribution(args.nims, args.src_path, args.dist_path,
            args.no_quiz_feedback, args.test_time)


if __name__ == '__main__':
    main()
