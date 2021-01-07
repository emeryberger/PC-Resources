#!/usr/bin/env python3
import csv
from datetime import datetime
from collections import defaultdict

# A script that takes into account which heavy PC members are assigned to
# each paper, their availability and produces as output the window that we
# can discuss this paper: a list of 30min slots that all the PC members
# are available to discuss it. Assume that all PC members without Doodle
# info are always available :)  For backup, please also calculate the
# windows we can discuss each paper with all PC members assigned -1.

# Inputs:
# All files need to be in the same directory currently. Requirements include:
DOODLE_AVAIL = 'Doodle_availability.csv' # Doodle poll. Downloaded Excel sheet as CSV
                                    # from email <-- important for processing.
                                    # Might need to make small processing changes
                                    # if the CSV file is different for the user
HEAVYPC_ASSIGNMENTS = 'heavypc-assignments.csv' # paper assignments for each
                                    # heavy PC member. This script currently
                                    # returns the windows of availability for
                                    # EVERY paper in this list. The list of
				    # papers actually being discussed should
				    # be set in papers.txt
PCEMAILS = 'emails.csv' # the email addresses and names of each heavy PC member.
                        # Important since the other two files above use a mixture
                        # of names and email addresses. This is a little brittle,
                        # requires names to be exact. I admit I made this by hand,
                        # if anyone is missing they will also need to be added
                        # by hand.

# outputs:
# csv in the following format:
#
# paper_number time1_hour time1_min time1_day ... timeN_hour timeN_min timeN_day
#
# where each time is the STARTING time of a 30 min slot where each member is
# available to discuss paper_number the whole time. Papers with asterisks mean
# that no time is available for all members, and therefore the times listed are
# with N-1 members.
#
# Examples:
# 2001  13 30 Tuesday 12 00 Tuesday 13 00 Tuesday 11 00 Tuesday 11 30
#      Tuesday 12 30 Tuesday
# 3333*  12 00 Tuesday 06 30 Tuesday 07 00 Tuesday 07 30 Tuesday 07 00
#       Wednesday 11 00 Tuesday 11 30 Tuesday 07 30 Wednesday
#
# Paper 2001 has 6 30min timeslots on Tuesday for EVERYONE to meet
# Paper 3333 doesn't have any timeslots where everyone can meet. It has
# 8 timeslots where N-1 members can meet (doesn't say who can't meet currently,
# but that would be straightforward to add)

timeslots_tues = []
timeslots_wed = []
timeslots = []

avail = {}

# read doodle poll availability and make dictionary with everyone's availability
with open(DOODLE_AVAIL, 'r') as file:
    reader = csv.reader(file)
    for i, row in enumerate(reader):
        if i == 5:
            # set up times lists in nice 24hr format
            timeslots_tues = [datetime.strftime(datetime.strptime("".join(j.split()[:2]), "%I:%M%p"), "%H %M Tuesday")
                            if j != '' else None for j in row[:35]]
            timeslots_wed = [datetime.strftime(datetime.strptime("".join(j.split()[:2]), "%I:%M%p"), "%H %M Wednesday")
                            if j != '' else None for j in row[35:]]
            # print(timeslots_tues)
            # print(timeslots_wed)
            timeslots = timeslots_tues + timeslots_wed
        if i > 5:
            avail[row[0]] = [timeslots[j] if 'OK' in k else '' for j,k in enumerate(row)]


# make dictionary of paper: PC assignments
emails = {}
with open(PCEMAILS, 'r') as file:
    reader = csv.reader(file)
    next(reader)
    for row in reader:
        emails[row[0]] = row[1].strip()

assign = defaultdict(lambda: [])

with open(HEAVYPC_ASSIGNMENTS, 'r') as file:
    reader = csv.reader(file)
    next(reader)
    for row in reader:
        assign[row[0]].append(emails[row[1]])


def check_inter(paper, assign):
    # find intersection for each paper
    # for each paper in assign, find intersection of each PC in avail
    s = None
    for person in assign[paper]:
        if person in avail:
        	if s:
        		s &= set(avail[person])
        	else:
        		s = set(avail[person])
    return list(s)

def check_union(paper, assign):
    # find the intersection for N-1 PCs
    # by taking the union of the intersections with one missing PC
    s = set([])
    for person in assign[paper]:
         x = set(assign[paper]) - set([person])
         s |= set(check_inter(paper, {paper: list(x)}))

    return list(s)

for paper in assign:
    s = check_inter(paper, assign)
    if len(s) > 1: # the empty string means no availability, so
                   # the intersection will be {''} if there is no good time
        print("{} {}".format(paper, ' '.join(s)))
    else:
        s = check_union(paper, assign)
        print("{}* {}".format(paper, ' '.join(s)))
