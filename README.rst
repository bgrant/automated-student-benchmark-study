README for ASB_Study
====================

:author: Robert Grant <robert.david.grant@utexas.edu>


Overview
--------
This distribution contains all the materials used for the Automated
Student Benchmarking study at the University of Texas.  The purpose of
this study was to get benchmarks of human learning on a curriculum to be
used to evaluate the learning of teachable software agents.  This
distribution is organized into three folders:

./student-materials
    Contains the lessons and reference material, quizzes, and simulator
    students use during the study

./teacher-materials
    Contains the subject-data-worksheet and  receipt forms for the study

./scripts
    Contains scripts to generate treatments for each subject, distribute
    them to study workstations, monitor subjects, and grade completed
    tests


Software Dependencies
---------------------
For the Python scripts:
 - python 2.7 or later (uses 'with' statement and argparse)
 - `dulwich <http://www.samba.org/~jelmer/dulwich/>`_
 - `markup.py <http://markup.sourceforge.net/>`_ (included)

For the Grader:
 - F#

For the Java simulator:
 - Java 1.5 or later


Study Architecture and Software Usage
-------------------------------------
The scripts provided in the `./scripts` directory are somewhat specific
to the organization of our testing lab.  For a full description of this
and how our studies were carried out, see the University of Texas
dissertation "Evaluating Instructable Software Agents Using Human
Benchmarks" by Robert David Grant.  

In brief, our lab contains a Linux server and several (six at last
count) Windows PCs, all on the same local-area network.  Each study
participant is assigned a Windows workstation; the Linux server is only
accessed by the study administrators.  All computers mount a network
attached storage (NAS) device which contains a folder specific to each
of the Windows workstations.  To make things simple we number each
workstation: Workstation 1 mounts the "station_1" folder on the NAS,
Workstation 2 mounts "station_2", and so on.

To prepare the workstations for a study group, 
  0) Make sure previous study data has been backed up
  1) Run `generate_study.py` on the server to create a study folder for
     a specific workstation (options determine treatments)
  2) Run `distribute_study.py` on the server to copy this folder to the
     correct workstation folder (this overwrites any data currently on
     the workstations)
  3) Monitor the students' progress using `station_monitor.py`
  4) Backup the study data with `backup_stations.py`

We keep the entire distribution in git (previously subversion).  The
`generate_study.py` script extracts the SHA1 hash of the current HEAD from the
repository and includes it in a `metadata.log` file in each generated folder.
In this way, we can determine exactly what version of the study a particular
participant took.

In our setup, the NAS is mounted on the server at

/media/asb_share

and the workstations have links to their particular folder ("station_1", for
example) on their desktop.

Each run (or benchmarking session containing one to six students) we give a
run_number, starting with 0 and increasing by one each time.  We assign each
subject a subject_id as a combination of run_number and workstation_number.
For example, the subject at Workstation 3 in the first run is subject 03, and
the subject at Workstation 1 in the 5th run is subject 41.

After a run is complete (all subjects finish and leave), we backup the data for
each station at

/media/asb_share/data/Run{$RUN_NUMBER}/station_{$STATION_NUMBER}

using `backup_stations.py`.

The `distribute_study.py` script overwrites any existing data on the
workstations, so it's important to remember to backup the data.


More Information
----------------
For more information, consult the University of Texas dissertation
"Evaluating Instructable Software Agents Using Human Benchmarks" by
Robert David Grant.

The main python and bash scripts have help, which you can access by
running the script with the -h or --help flags.  Several convenience
scripts are included without help (such as dist_all.sh), but these are
short and easy to figure out from the source.  All of the scripts are
relatively simple and broken into logical functions, so I encourage you
to look at the source if you have questions.


Acknowledgements
----------------
Research related to this software was sponsored by AFRL under contract
FA8650-07-C-7722.

Thanks to my fellow researchers at UT:  David DeAngelis, Dan Luu, and
Matthew Berland, and my advisor Dewayne E. Perry for their contributions
to this project.  Thanks to our colleagues at BAE Systems, Cycorp, Inc.,
Stottler Henke Associates, Inc., Sarnoff Corporation, and Teknowledge
Corporation for their collaboration in developing the curricula and
testing materials, and to the many study participants at The University
of Texas at Austin.
