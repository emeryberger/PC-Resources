# find-topicless.py: finds PC members who haven't set topic preferences
#   - used for getting a list of such PC members to send an email to them
# Author: Jay Lorch <jaylorch@gmail.com>
# Released into the public domain.

import argparse
import csv
import sys
import os
import re

parser = argparse.ArgumentParser('find-topicless')
parser.add_argument('conference', help='conference name used as a prefix of csv file names exported by HotCRP, e.g., osdi21')

args = parser.parse_args()
if not args.conference:
    parser.print_help()
    sys.exit(-1)

def describe_how_to_get_pcinfo(conference, file_name):
    print('Could not find a file in the current directory named ' + file_name)
    print('To get this file, do the following:')
    print('1) Visit https://' + conference + '.usenix.hotcrp.com/users?t=pc (the domain might be different for a non-USENIX conference).')
    print('2) Scroll to the bottom of the page.')
    print('3) Look for "Select people (or select all X)" and click "select all X".')
    print('4) To the right of that, after "Download", select "PC info" from the dropdown menu.')
    print('5) Click the "Go" button to the right of that dropdown.')
    print('6) Copy the ' + conference + '-pcinfo.csv file downloaded this way to this directory.')

def find_topicless():
    infile_name = args.conference + "-pcinfo.csv"

    if not os.path.exists(infile_name):
        describe_how_to_get_pcinfo(args.conference, infile_name)
        sys.exit(-1)

    topicless_pc_list = []
    pc_count = 0
    with open(infile_name, 'r') as infile:
        reader = csv.DictReader(infile, delimiter=',')
        for row in reader:
            pc_count += 1
            topics = [column for column in row if re.search(r'^topic: ', column) and row[column]]
            if len(topics) == 0:
                topicless_pc_list.append(row['first'] + ' ' + row['last'] + ' <' + row['email'] + '>')

    if len(topicless_pc_list) == 0:
        print('Congratulations!  All of the ' + str(pc_count) + ' members of the PC have set topic preferences.')
    else:
        print('These are the ' + str(len(topicless_pc_list)) + ' PC members who have not yet set topic preferences:')
        print('')
        print(';\n'.join(topicless_pc_list))
                    

find_topicless()
