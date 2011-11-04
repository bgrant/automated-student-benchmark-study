#! /usr/bin/env bash

# :author: Robert Grant <robert.david.grant@utexas.edu> 
#
# :copyright:
#     Copyright 2011 The University of Texas at Austin
# 
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
# 
#        http://www.apache.org/licenses/LICENSE-2.0
# 
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.

if [ $# -ne 1 ] || [ $1 == "-h" ] || [ $1 == "--help" ]
then
    echo "usage: `basename $0` [-h] path_to_stationdir"
    echo """
A simple grading script that allows monitoring of subjects' progress
reporting of approximate scores afterwards.  It's not guaranteed to be
accurate, and a better one should be written that actually uses the SHAI
grading program and parses the log files.  Outputs JSON data.

positional arguments:
  path_to_stationdir    the folder containing station information 
                        (e.g., /media/asb_share/stations/station_1)

optional arguments:
  -h, --help            show this help message and exit
"""
    exit $E_BADARGS
fi

pre_total=$(find $1/lib/pretest_simulator -name *.xml -print0 | xargs -0 tail -n4 | grep -c CONNECTION)
pre_good=$(find $1/lib/pretest_simulator -name *.xml -print0 | xargs -0 tail -n4 | grep -c GOOD)

quiz_path="$1/lib/quizzes"
#quizzes_done=$(find $1/lib/quizzes -name *.log -print0 | xargs -0 cat | grep -c score)
#quizzes=$(find $1/lib/quizzes -name *.log -print0 | xargs -0 cat | grep score | cut -d: -f2 | cut -d, -f1)
#quiz_names=$(find $1/lib/quizzes -name *.log -print)

post1_total=$(find $1/lib/test_simulator -name *.xml -print0 | xargs -0 tail -n4 | grep -c CONNECTION)
post1_good=$(find $1/lib/test_simulator -name *.xml -print0 | xargs -0 tail -n4 | grep -c GOOD)

post2_total=$(find $1/lib/penultimate_simulator -name *.xml -print0 | xargs -0 tail -n4 | grep -c CONNECTION)
post2_good=$(find $1/lib/penultimate_simulator -name *.xml -print0 | xargs -0 tail -n4 | grep -c GOOD)

af_total=$(find $1/lib/final_simulator -name *.xml -print0 | xargs -0 tail -n4 | grep -c CONNECTION)
af_good=$(find $1/lib/final_simulator -name *.xml -print0 | xargs -0 tail -n4 | grep -c GOOD)

echo "{"
echo "\"Pre-Test\": \"$pre_good/$pre_total\","
#echo "\"Quizzes tried\": $quizzes_done,"
#echo "\"Quiz Names\": [$quiz_names],"
#quiz_scores=$(
#for x in $quizzes; do
#    echo -n " $x,"
#done
#)
#quiz_scores=${quiz_scores:0:${#quiz_scores}-1}
#echo "\"Quiz Scores\": [$quiz_scores],"
for x in "1_1" "2_3" "2_6" "3-4_3" "3-4_6"; do
    scores=""
    quiz_scores=""
    if [ -e $quiz_path/*$x*.log ]; then
        scores=$(cat $quiz_path/*$x*.log | grep score | cut -d: -f2 | cut -d, -f1)
        quiz_scores=$( for y in $scores; do echo -n " $y,"; done)
        quiz_scores=${quiz_scores:1:${#quiz_scores}-2}
    fi
    echo "\"Quiz $x\": \"$quiz_scores\","
done

echo "\"Post-Test-1\": \"$post1_good/$post1_total\","
echo "\"Post-Test-2\": \"$post2_good/$post2_total\","
echo "\"Final-Test\": \"$af_good/$af_total\""
echo "}"
