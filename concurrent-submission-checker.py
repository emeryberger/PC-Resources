# concurrent-submission-checker.py: finds papers with the same title submitted to two conferences
#   - used for checking for concurrent submissions to conferences with overlapping review periods
# Author: Jay Lorch <jaylorch@gmail.com>
# Released into the public domain.

import argparse
import csv
import sys
import os
from collections import defaultdict
from hashlib import sha256

parser = argparse.ArgumentParser('concurrent-submission-checker', epilog="""
Normally, this script is used as follows:

The chair of the first conference runs it to get title hashes, and
sends the resulting file to the chair of the second conference.

The chair of the second conference runs it to get title hashes, then
runs it again with --other-conference to compare the two sets of title
hashes.
""")
parser.add_argument('--conference', help='conference name used as a prefix of csv file names exported by HotCRP, e.g., nsdi21fall')
parser.add_argument('--other-conference', help='(optional) other conference name to compare to; if you just want to produce title hashes to send to another chair, leave out this argument')

args = parser.parse_args()
if not args.conference:
    parser.print_help()
    sys.exit(-1)

def canonicalize_title(title):
    return ''.join([c.upper() for c in title if c.isalnum()])

def describe_how_to_get_data(conference, file_name):
    print('Could not find a file in the current directory named ' + file_name)
    print("To get this file, do the following:")
    print("1) Visit https://" + conference + ".usenix.hotcrp.com/search?q=&t=act (the domain might be different for a non-USENIX conference).")
    print("2) If you've already notified some papers' authors of early rejection, use a custom search that excludes such papers.")
    print("3) Scroll to the bottom of the page.")
    print('4) Look for "Select papers (or select all X)" and click "select all X".')
    print('5) To the right of that, after "Download", select "CSV" from the dropdown menu.')
    print('6) Click the "Go" button to the right of that dropdown.')
    print('7) Copy the ' + conference + '-data.csv file downloaded this way to this directory.')

def describe_how_to_get_titlehashes(conference, file_name):
    print('Could not find a file in the current directory named ' + file_name)
    print('To get the title hashes of the papers from conference ' + conference + ',')
    print('run this script with --conference=' + conference + ' and with no --other_conference argument.')

def hash_titles():
    infile_name = args.conference + "-data.csv"
    outfile_name = args.conference + '-titlehashes.csv'

    if not os.path.exists(infile_name):
        describe_how_to_get_data(args.conference, infile_name)
        sys.exit(-1)

    with open(infile_name, 'r') as infile:
        with open(outfile_name, 'w') as outfile:
            reader = csv.DictReader(infile, delimiter=',')
            writer = csv.DictWriter(outfile, delimiter=',', fieldnames=['ID', 'TitleHash'])
            writer.writeheader()
            for row in reader:
                paper_id = row['ID']
                title = row['Title']
                title_hash = sha256(canonicalize_title(title).encode()).hexdigest()
                writer.writerow({'ID' : paper_id, 'TitleHash' : title_hash})

    print('Title hashes saved to ' + outfile_name)
    print('Send that file to the chairs of the other conference so they can check for concurrent submissions.')

def compare_conferences():
    infile1_name = args.conference + '-titlehashes.csv'
    infile2_name = args.other_conference + '-titlehashes.csv'

    if not os.path.exists(infile1_name):
        describe_how_to_get_titlehashes(args.conference, infile1_name)
        sys.exit(-1)

    if not os.path.exists(infile2_name):
        describe_how_to_get_titlehashes(args.other_conference, infile2_name)
        sys.exit(-1)

    ids_for_hash = defaultdict(list)
    with open(infile1_name, 'r') as infile1:
        reader = csv.DictReader(infile1, delimiter=',')
        for row in reader:
            paper_id = row['ID']
            title_hash = row['TitleHash']
            ids_for_hash[title_hash].append(paper_id)

    potential_overlaps = []
    with open(infile2_name, 'r') as infile2:
        reader = csv.DictReader(infile2, delimiter=',')
        for row in reader:
            paper_id2 = row['ID']
            title_hash = row['TitleHash']
            if title_hash in ids_for_hash:
                for paper_id in ids_for_hash[title_hash]:
                    potential_overlaps.append({args.conference + '-ID' : paper_id, args.other_conference + '-ID' : paper_id2})

    if len(potential_overlaps) > 0:
        outfile_name = args.conference + '-' + args.other_conference + '-potentialoverlaps.csv'
        with open(outfile_name, 'w') as outfile:
            writer = csv.DictWriter(outfile, delimiter=',', fieldnames=[args.conference + '-ID', args.other_conference + '-ID'])
            writer.writeheader()
            for entry in potential_overlaps:
                writer.writerow(entry)
        print('Found ' + str(len(potential_overlaps)) + ' title overlaps betwen ' + args.conference + ' and ' + args.other_conference + '.')
        print('Saved those potential overlaps in ' + outfile_name)
    else:
        print('Great news:  Found no title overlaps betwen ' + args.conference + ' and ' + args.other_conference + '.')

if args.other_conference:
    compare_conferences()
else:
    hash_titles()

