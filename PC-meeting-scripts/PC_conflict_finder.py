#!/usr/bin/env python3

# Reports papers for which each PC co-chair is conflicted.

PC_cochair_emails = ["emery@cs.umass.edu", "kozyraki@stanford.edu"]

import csv


def find_conflicts(conflicts, filename):
    result = {c: [] for c in conflicts}

    with open(filename) as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            paper = row[0]
            conflict = row[4]
            if conflict in conflicts:
                result[conflict] += [paper]
    return result


if __name__ == '__main__':
    PC_cochair_emails = [
        'emery@cs.umass.edu',
        'kozyraki@stanford.edu'
    ]
    result = find_conflicts(PC_cochair_emails, 'conflicts.csv')
    for c in result:
        print("{} {}".format(c, " ".join(result[c])))
