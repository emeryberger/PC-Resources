#!/usr/bin/env python3
#   - used for counting words in review comments (not part of review form)
# Authors: Jon Howell <jonh@jonh.net>
#          Jay Lorch <jaylorch@gmail.com>
#          Angela Demke Brown <demke@cs.toronto.edu>
# Released into the public domain.

import argparse
import re
import sys


parser = argparse.ArgumentParser('comment-word-counter', epilog="""
This script takes reviews written for submissions to a
conference and counts the number of post-review comments and 
the number of words written in those comments.
""")
parser.add_argument('conference', help='conference name used as a prefix of -papers.zip file name exported by HotCRP, e.g., osdi21')

def describe_how_to_get_reviews(conference, file_name):
    print('Could not find a file in the current directory named ' + file_name)
    print('To get this file, do the following:')
    print('1) Visit https://' + conference + '.usenix.hotcrp.com/search?q=&t=s (the domain might be different for a non-USENIX conference).')
    print('2) Scroll to the bottom of the page.')
    print('3) Look for "Select papers (or select all X)" and click "select all X".')
    print('4) To the right of that, after "Download", select "Reviews (text)" from the dropdown menu.')
    print('5) Click the "Go" button to the right of that dropdown.')
    print('6) Copy the ' + conference + '-reviews.txt file downloaded this way to this directory.')

class CommentCounter:
    def __init__(self, conference):
        self.conference = conference

    def parse(self, paper_file):
        in_comment = False
        skip_next_line = False
        for line in paper_file:
            line = line.strip()

            if skip_next_line:
                skip_next_line = False
                if not line.startswith("-----"):
                    print("    --> expected skipped line to always be ----")
                continue
            
            # Does line mark the start of a comment?
            if line.startswith("Comment @"):
                in_comment = True
                skip_next_line = True
                self.comment_count += 1
                continue

            # Does line mark the start of the author response?
            if line.startswith("Response by"):
                in_comment = False
                continue

            # Does line mark the end of the current review?
            if line.startswith("* * * * * * * * * * * * * * * * * * * * * * *"):
                in_comment = False
                continue

            # Count words in line if we're in a comment block currently
            if in_comment:
                line_words = len(line.split())
                self.comment_words += line_words

    
    def run(self):
        self.comment_count = 0
        self.comment_words = 0
        filename = self.conference + "-reviews.txt"
        try:
            with open(filename,'r') as f:
                self.parse(f)
            f.close()

        except IOError:
            print("Could not read file " + filename)
            describe_how_to_get_reviews(self.conference, filename)
            sys.exit()
            
        print("Total discussion comments %d, total discussion comment words %d" % (self.comment_count,self.comment_words))
        print("Note that this *does* include discussions you're conflicted with, since those *do* appear in %s" % (filename))
        

args = parser.parse_args()
comment_ctr = CommentCounter(args.conference)
comment_ctr.run()
