#!/usr/bin/env python3

# Returns the windows of time for which the co-chairs are each available.

pc_cochairs = ["Emery Berger", "Christos Kozyrakis"]
DOODLE_AVAIL = 'Doodle_availability.csv'

import csv
from datetime import datetime
from collections import defaultdict


timeslots_tues = []
timeslots_wed = []
timeslots = []

avail = {}

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
            for chair in pc_cochairs:
                if row[0] == chair:
                    avail[row[0]] = [timeslots[j] if 'OK' in k else '' for j,k in enumerate(row)]
                    break

for chair in pc_cochairs:
    print("Chair:{} -- {}\n".format(chair, ' '.join(avail[chair])))
