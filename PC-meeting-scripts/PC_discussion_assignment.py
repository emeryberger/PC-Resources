#!/usr/bin/env python3
# takes in a list of timeslots for each paper
# and a list of conflicts of special people

from functools import cmp_to_key
import PC_conflict_finder

TIME_WINDOW = 30  # minutes, the availability window length

TIME_WINDOWS_FILE = 'times.txt'  # should be the output of PC_discussion_windows.py

PC_TIMES_FILE = 'pc_avail.txt'  # should be the output of  PC_windows.py

PAPERS_FILE = 'papers.txt'      # should be the list of papers to schedule,
                                # one per line

DURATION = 5  # minutes, the time to discuss each paper


DAYS = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
        'Saturday']  # Days of the week, you can ignore


def timepair_to_minutes(time, duration):
    start = int(time[0]) * 60 + int(time[1])
    start += 24 * 60 * DAYS.index(time[2])  # skip days
    result = []
    cur = start
    while cur < start + TIME_WINDOW:
        result += [cur]
        cur += duration
    return result


def process_papers(schedule, duration, pc_conflicts, pc_times):
    result = []
    for row in schedule:
        paper = row[0]
        toadd = [paper]
        times = []
        i = 1
        while i < len(row):
            times += timepair_to_minutes(row[i:i+3], duration)
            i += 3
        toadd += works_for_specials(paper, times, pc_conflicts, pc_times)
        result += [toadd]
    return result


def make_schedule(schedule, duration, pc_conflicts, pc_times):
    papers = process_papers(schedule, duration, pc_conflicts, pc_times)
    # put the papers in order of number of free time slots
    papers.sort(key=cmp_to_key(lambda x, y: 1 if len(x) > len(y) else -1))
    # print("solving {}".format(papers))
    return try_schedule(papers, 0, {})


def works_for_specials(paper, times, pc_conflicts, pc_times):
    s = set([])
    for i in range(0, len(pc_times)):
        conflict = pc_conflicts[i]
        if paper.replace('*', '') not in conflict:
            s |= set(pc_times[i])
    if s:
        return list(set(times) & s)
    else:
        print('Paper {} has no available PC chair'.format(paper))
        return times 


def try_schedule(papers, left, done):
    if left >= len(papers):
        return done

    to_schedule = papers[left]
    paper = to_schedule[0]
    possibilities = to_schedule[1:]
    # print("trying {}".format(paper))
    for possibility in possibilities:
        if possibility in done.values():
            continue  # skip used times

        done[paper] = possibility
        works = try_schedule(papers, left + 1, done)
        if works:
            return works
    return None


def convert_back(results):
    for paper in results:
        day = 0
        hour = 0
        time = results[paper]
        while time >= 24 * 60:
            time -= 24 * 60
            day += 1
        while time >= 60:
            time -= 60
            hour += 1
        print("{} {} at {}:{:02}".format(paper, DAYS[day], hour, time))


if __name__ == '__main__':
    papers = []
    pc_times = []
    allowed_papers = []
    with open(PAPERS_FILE) as f:
        for row in f:
            row = row.strip().replace('*', '')
            allowed_papers.append(row)
    with open(TIME_WINDOWS_FILE) as f:
        for row in f:
            row = row.strip().split()
            if row[0].replace('*', '') in allowed_papers:
                papers.append(row)
    with open(PC_TIMES_FILE) as f:
        for row in f:
            row = row.strip().split()
            i = 0
            times = []
            while i < len(row):
                times += timepair_to_minutes(row[i:i+3], DURATION)
                i += 3
            pc_times.append(times)
    conflicts = conflict_finder.find_conflicts(PC_cochair_emails, 'conflicts.csv')
    pc_conflicts = [conflicts[c] for c in PC_cochair_emails]

    convert_back(make_schedule(papers, DURATION, pc_conflicts, pc_times))
