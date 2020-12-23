# diff-unexplained-conflicts.py: find difference between unexplained-conflicts lists.
#   - used for finding unexplained conflicts that have arisen since last time they
#     were searched for.
# Authors: Jay Lorch <jaylorch@gmail.com>
# Released into the public domain.

import argparse
import csv
import re
import smtplib
import sys
import os
import time
from collections import defaultdict

parser = argparse.ArgumentParser('diff-unexplained-conflicts', epilog="""
Normally, this script is used as follows:

After the abstract-registration deadline, a chair runs the
find-unexplained-conflicts script to obtain a list of unexplained
conflicts in a file named, e.g.,
18nov/osdi21-unexplainedconflicts.csv.

Then, the chair uses the time before the paper-submission deadline
to root out improperly-declared conflicts.

However, it may be that people declare more improper conflicts later.
So, after the paper-submission deadline (when authors can't change
their conflicts any more), the chair runs find-unexplained-conflicts.py
one more time to get another file, e.g.,
25nov/osdi21-unexplainedconflicts.csv.

Finally, the chair runs this script to get a list of just the
unexplained conflicts from the latter file, e.g., with

% diff-unexplained-conflicts.py 18nov/osdi21-unexplainedconflicts.csv \
     25nov/osdi21-unexplainedconflicts.csv
""")

parser.add_argument('earlier_file', help='first file, e.g., 18nov/osdi21-unexplainedconflicts.csv')
parser.add_argument('later_file', help='later file, e.g., 25nov/osdi21-unexplainedconflicts.csv')

class ConflictsDiffer:
    def __init__(self, earlier_file, later_file):
        self.earlier_file = earlier_file
        self.later_file = later_file

    def run(self):
        self.read_earlier_file()
        self.read_later_file()

    def read_earlier_file(self):
        if not os.path.exists(self.earlier_file):
            print("Could not find file %s" % (self.earlier_file))
            sys.exit(-1)

        self.earlier_conflicts = defaultdict(set)
        with open(self.earlier_file, 'r') as infile:
            reader = csv.DictReader(infile, delimiter=',')
            for row in reader:
                paper_id = row["paper"]
                pcmember = row["email"]
                self.earlier_conflicts[paper_id].add(pcmember)

    def read_later_file(self):
        if not os.path.exists(self.later_file):
            print("Could not find file %s" % (self.later_file))
            sys.exit(-1)

        field_names = ["paper", "email", "uid", "conflicttype", "explanations"]
        writer = csv.DictWriter(sys.stdout, delimiter=',', fieldnames=field_names)
        writer.writeheader()

        with open(self.later_file, 'r') as infile:
            reader = csv.DictReader(infile, delimiter=',')
            for row in reader:
                paper_id = row["paper"]
                pcmember = row["email"]
                if paper_id not in self.earlier_conflicts or pcmember not in self.earlier_conflicts[paper_id]:
                    writer.writerow(row)

args = parser.parse_args()

differ = ConflictsDiffer(args.earlier_file, args.later_file)
differ.run()
