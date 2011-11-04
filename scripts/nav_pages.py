#! /usr/bin/env python

"""
Functions to generate the study-navigation web page for a student in the
Automated Student Benchmark study. 

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


from os import path
import re
from glob import glob
import random

import markup
from markup import oneliner as e


ALLFAULT_PROBABILITY = 1.1


def translate_treatment(nims):
    """
    Takes a list of nim abbreviations and returns the dictionary keys for the
    paths to the corresponding slides.

    :param nims: a list of 't','e', and/or 'f'.
    :return: a list of keys for the `paths` dictionary for the corresponding
        slides
    """
    treatment = {
            't': 'T',
            'e': 'E',
            'f': 'BF',
        }

    return [treatment[x] for x in nims if x in treatment]


def generate(nims, no_quiz_feedback='False', test_time=300 ):
    """
    Generate the HTML page based on the list of `nims` to be passed to `treatment`.

    NOTE: Must be called within directory containing materials!  This is done
    by `generate_study.py`.  Probably should rewrite to take paths as
    arguments.

    :param nims: list containing {t,e,f}
    :param test_time: time for a single test fault scenario
    :param no_quiz_feedback: turn off showing quiz scores

    :return: HTML page as markup object
    """

    test_time_minutes = format(test_time/60.0, '.1f')

    page = markup.page()

    title = "Automated Student Benchmark Study"
    page.init(title=title)
    page.h1(title)

    page.p("""Please follow the instructions on this page.  The first few
    linked documents (under the heading 'Reference Material') you may have
    already seen; they are provided for your reference.""")
    page.p("""REMEMBER: You may refer to the material under 'Reference' at any
    time, but you may <b>not</b> refer to the 'Curriculum' material during
    quizzes or tests.""")

    page.h2("Reference Material")
    page.ul()
    page.li( e.a("Cover Letter", href=path.join('reference',
        'cover-letter.pdf'), target='blank') )
    page.li( e.a("Student Instructions", href=path.join('reference',
        'student-instructions.pdf'), target='blank') )
    page.li( e.a("Background Knowledge", href=path.join('reference',
        'background-knowledge.pdf'), target='blank') )
    page.ul.close()

    page.h2("Pre-Test")
    page.p("In this pre-test you will be given " + test_time_minutes + 
           " minutes to diagnose and fix the satellite tracking rig.")
    page.p(""" Please begin by double-clicking the 'Pre-Test' link in the main
    study folder to open the pre-test simulator.  Click 'Start Simulation' when
    you are ready to begin the timed test.  After the timer runs out and the
    simulation ends, please close the simulator and return to this page.""")

    # Get the rung info
    curriculum_path = 'curriculum'
    rung_paths = glob( path.join(curriculum_path, '*') )
    rung_paths.sort()
    rung_names = [path.split(rung)[1] for rung in rung_paths]

    # Glob the paths to the T, E, and BF slides by their names
    slides_path = {}
    for nim in ['T', 'E', 'BF']:
        slide_path = glob( path.join(curriculum_path, '*', '*', '*' + nim
            + '_slides*.pdf') )
        slides_path[nim] = sorted(slide_path)

    # Glob the quiz files
    if no_quiz_feedback:
        quiz_paths = glob( path.join('quizzes', 'Rung*no_feedback.html') )
    else:
        quiz_paths = glob( path.join('quizzes', 'Rung*yes_feedback.html') )
    quiz_paths.sort()

    quiz_full_names = [path.splitext(path.split(filename)[1])[0] for filename
            in quiz_paths]
    pattern = "(Rung_\d(-\d)?_\d)_.+_feedback"
    quiz_names = [re.search(pattern, full_name).groups()[0] for full_name in
            quiz_full_names]

    quiz_dict = dict( zip(quiz_names, quiz_paths) )

    page.h2("Curriculum")
    page.p("""Please complete the following lessons and quizzes in order. When
    you have finished with one document, close the window or tab and move on to
    the next. You are allowed to take notes, either on the scratch paper
    provided or in Notepad.""")  
    page.p("""Feedback lessons require you to interact with the simulator. To
    launch the simulator for practice, double-click the shortcut labeled
    'Simulator' in the main study folder.""")
    #"""For Rung 6_4 only, instead double-click the shortcut labeled
    #'Realtime-Simulator'.""")

    nim_names = translate_treatment(nims)
    nim_tuples = zip(*[slides_path[x] for x in nim_names])

    for (rung_name, nim_set) in zip(rung_names, nim_tuples): 
        page.h3(rung_name)
        page.ul()
        for nim in nim_set:
            file_name = path.split(nim)[1]
            # pull out the descriptive rung name
            match = re.search("(Rung_\d(-\d)?_\d_)?(.+)_slides", file_name)
            desc_name = match.groups()[-1] # we want the last group
            page.li( e.a(desc_name, href=nim, target='blank') )
        page.ul.close()

        if rung_name in quiz_names:
            page.a(e.h3("Quiz"), href=quiz_dict[rung_name], target='blank')

    page.h2("Post-Test 1")
    page.p("In this post-test you will be given " + test_time_minutes +
    """ minutes per scenario to diagnose and fix any faults in the satellite
    tracking rig (if any exist), for each of five scenarios.""")
    page.p("""Please begin by double-clicking the 'Post-Test-1' link in the main
    study folder to open the post-test simulator.  Click 'Start Simulation'
    when you are ready to begin a scenario.  After the timer runs out and the
    simulation ends, please click 'Start Simulation' again to begin the next
    scenario.  After you have completed five scenarios, please close the
    simulator and return to this page.""")

    page.h2("Post-Test 2")
    page.p("In this post-test you will be given " + test_time_minutes + 
    """ minutes to diagnose and fix any faults in the satellite tracking rig
    (if any exist) for a single scenario.""")
    page.p("""Please begin by double-clicking the 'Post-Test-2' link in the
    main study folder to open the post-test simulator.  Click 'Start
    Simulation' when you are ready to begin the scenario.  After the timer runs
    out and the simulation ends, please close the simulator and return to this
    page.""")

    # give the all-fault case with a certain probability
    if random.uniform(0, 1) < ALLFAULT_PROBABILITY:
        page.h2("Final Test")
        page.p("In this final test you will be given " + test_time_minutes +
        """ minutes to diagnose and fix the satellite tracking rig.""")
        page.p(""" Please begin by double-clicking the 'Final-Test' link
        in the main study folder to open the additional-test simulator.  Click
        'Start Simulation' when you are ready to begin the timed test.  After
        the timer runs out and the simulation ends, please close the simulator
        and return to this page.""")


    page.p("""You are finished.  Please raise your hand to alert the study
    supervisor.""")

    return page


def write(nims, filename='ASB_Study.htm', no_quiz_feedback='False',
        test_time=300):
    """
    Write out the HTML navigation page.

    :param nims: a list of 't','e', and/or 'f'.
    :param filemame: file name to write HTML page to
    :param no_quiz_feedback: boolean indication whether or not subjects should
    be given feedback on quizzes
    :param test_time: time for a single test fault scenario
    """

    page = generate(nims, no_quiz_feedback, test_time)
    with open(filename, 'w') as filehandle:
        filehandle.write(str(page))
