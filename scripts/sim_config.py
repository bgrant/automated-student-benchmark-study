#! /usr/bin/env python

"""
Functions to generate the simulator config files for a student in the Automated
Student Benchmark study.

:author: Dave DeAngelis <dave@lips.utexas.edu>
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


import time, random


def generate_gsConfig(configarg, timestamp, test_time=300):
    """
    Return contents for a gsConfig.txt file based on configuration.

    :param configarg: 'feedback', 'realtime', 'test', 'pretest', 'penultimate',
    'final'
    :param timestamp: string placed in header comment of file

    :return: string of contents for a gsConfig.txt file based on configuration.  
    """
    constants = ('nextTaskTimeSeconds=60',
                 'hideFaultNames=true',
                 'showFastForward=true',
                 'showStatusPanel=false',)
    
    configurations = {
        'feedback': (
            'testing=false',
            'realTime=false',
            ) + constants,
        'realtime': (
            'testing=false',
            'realTime=true',
            ) + constants,
        'test': (
            'testing=true',
            'realTime=false',
            'timeLimitEnabled=true',
            'timeLimitSeconds=' + str(test_time),
            ) + constants,
        }
    configurations['pretest'] = configurations['test'] 
    configurations['penultimate'] = configurations['test'] 
    configurations['final'] = configurations['test'] 

    return "\n".join( (timestamp,) + (configurations[configarg]) )
    

def generate_tests(selected_faults):
    """
    Return contents for a gsTest.txt file given a tuple of faults

    :param selected_faults: tuple of tuple of faults; a subset of the
    fault_list in gsTests

    :return: string containing contents for a gsTests.txt file
    """

    faults = list(selected_faults)
    random.shuffle(faults)
    line_list = []
    for num, fault in enumerate(faults):
        for line in fault:
            line_list.append(str(num+1) + line)

    return "\n".join(line_list)
                

def generate_gsTests(testarg, timestamp):
    """
    Return contents for a gsTest.txt file based on configuration.

    :param testarg: 'feedback', 'realtime', 'test', 'pretest', 'final'
    :param timestamp: string placed in header comment of file

    :return: string containing contents for a gsTests.txt file based on
    configuration
    """

    fault_list = (
        # Base faults for pre- and post-test
        ('=Antenna_Motion_Error', '_Modifier=0', '_Presented=false'),
        ('=Baseband_Misconfiguration', '_Modifier=0', '_Presented=false'),
        ('=Antenna_Intrack_Pointing_Error', '_Modifier=5', '_Presented=false'),
        ('=Antenna_Azimuth_Pointing_Error', '_Modifier=0', '_Presented=false'),
        ('=Antenna_Elevation_Pointing_Error', '_Modifier=0', '_Presented=false'),
        ('=Baseband_Hangup', '_Modifier=0', '_Presented=false'),
        # None fault only included in post-test
        ('=None', '_Modifier=0', '_Presented=false'),
        # Harder version of Antenna Intrack Error for penultimate test
        ('=Antenna_Intrack_Pointing_Error', '_Modifier=0', '_Presented=false'),
        # Multi-Fault Case
        (', '.join(('=' + 
            'Antenna_Motion_Error', 
            'Baseband_Misconfiguration',
            'Antenna_Intrack_Pointing_Error', 
            'Antenna_Azimuth_Pointing_Error',
            'Baseband_Hangup')),
            '_Modifier=0, 0, 0, 0, 0', '_Presented=false')
    )

    configurations = {
        'feedback': "Not a testing configuration.",
        'realtime': "Not a testing configuration.",
        'pretest': generate_tests( (random.choice(fault_list[:6]),) ),
        'test': generate_tests( random.sample(fault_list[:7], 5) ),
        'penultimate': generate_tests( (fault_list[-2],) ),
        'final': generate_tests( (fault_list[-1],) ),
    }

    return timestamp + "\n" + configurations[testarg]
    

def write(config, test_time=300):
    """
    Write out a gsTests.txt and gsConfig.txt file based on configuration.
    Place a timestamp at the top of each.

    :param testarg: 'feedback', 'realtime', 'test', 'pretest', 'penultimate',
    'final'
    :param test_time: time for a final test scenario in seconds
    """
    timestamp = '## Generated on: ' + time.asctime()

    with open('gsConfig.txt', 'w') as gsConfig:
        gsConfig.write( generate_gsConfig(config, timestamp, test_time) )

    with open('gsTests.txt', 'w') as gsTests:
        gsTests.write( generate_gsTests(config, timestamp) )
