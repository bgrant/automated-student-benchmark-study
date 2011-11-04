#! /usr/bin/env python

"""
Functions to log the metadata for a study.

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


import os
import json
import dulwich

def package(nims, no_quiz_feedback, test_time):
    """
    Get distribution metadata and package it as a dictionary.

    :param nims: list of NIMs given to generate_study on the command line
    :param no_quiz_feedback: boolean option given to generate_study on the command line
    :param test_time: post-test time in seconds given to generate_study on the command line 

    :returns: dictionary containing study_revision, nims, no_quiz_feedback, and
    test_time
    """

    # Save git HEAD SHA1 as study revision identifier
    repo = dulwich.repo.Repo('..')

    metadata = {
            "study_revision": repo.head(),
            "nims": nims,
            "no_quiz_feedback": no_quiz_feedback,
            "test_time": test_time
            }

    return metadata


def write(dist_path, nims, no_quiz_feedback, test_time):
    """
    Write out a metadata.log file in JSON format.

    :param dist_path: path to distribution
    :param nims: list of NIMs given to generate_study on the command line
    :param no_quiz_feedback: boolean option given to generate_study on the command line
    :param test_time: post-test time in seconds given to generate_study on the command line 
    """
    logpath = os.path.join(dist_path, 'metadata.log')
    with open(logpath, 'w') as logfile:
        json.dump( package(nims, no_quiz_feedback, test_time), logfile )
