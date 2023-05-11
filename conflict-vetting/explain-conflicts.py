# explain-conflicts.py: finds author-declared conflicts that can't be explained
#   - used for checking for bogus conflicts / conflict engineering.
# Authors: Jay Lorch <jaylorch@gmail.com>
#          Emery Berger <emery.berger@gmail.com>
#          Jon Howell <jonh.conflict-vetter@jonh.net>
# Released into the public domain.

import argparse
import csv
import re
import sys
import os
from collections import defaultdict

parser = argparse.ArgumentParser('explain-conflicts', epilog="""
Normally, this script is used as follows:

First, a chair makes a file *-extraaffiliations.csv where * is the
conference name, listing any extra affiliations that they know about
for paper authors. If they know of no such extra affiliations, they
can skip this step. The first line of that csv file should be:
email,affiliation

Then, a chair runs this explain-conflicts.py script to obtain a list of
unexplained conflicts in a file named *-unexplainedconflicts.csv and a
list of explained conflicts in a file named *-explainedconflicts.csv.

Then, the chair manually looks over the unexplained-conflicts file to
remove any they understand and can explain.

Then, the chair runs the mail-pc-re-conflicts.py script to ask PC
members to look over the unexplained conflicts and confirm ones that
they also can't explain.  The chairs wait for a while for the PC to
respond.

Finally, the chair runs the investigate-conflicts.py script to
get a list of unexplained conflicts that PC members report, so they
can investigate.
""")
parser.add_argument('--conference', help='conference name used as a prefix of csv file names exported by HotCRP, e.g., osdi21')
parser.add_argument("--hash-salt", help="hash salt, for obscuring paper IDs")

def describe_how_to_get_authors(conference, file_name):
    print('Could not find a file in the current directory named ' + file_name)
    print('To get this file, do the following:')
    print('1) Visit https://' + conference + '.usenix.hotcrp.com/search?q=&t=act(the domain might be different for a non-USENIX conference).')
    print('2) Scroll to the bottom of the page.')
    print('3) Look for "Select papers (or select all X)" and click "select all X".')
    print('4) To the right of that, after "Download", select "Authors" from the dropdown menu.')
    print('5) Click the "Go" button to the right of that dropdown.')
    print('6) Copy the ' + conference + '-authors.csv file downloaded this way to this directory.')

def describe_how_to_get_pcconflicts(conference, file_name):
    print('Could not find a file in the current directory named ' + file_name)
    print('To get this file, do the following:')
    print('1) Visit https://' + conference + '.usenix.hotcrp.com/search?q=&t=act (the domain might be different for a non-USENIX conference).')
    print('2) Scroll to the bottom of the page.')
    print('3) Look for "Select papers (or select all X)" and click "select all X".')
    print('4) To the right of that, after "Download", select "PC conflicts" from the dropdown menu.')
    print('5) Click the "Go" button to the right of that dropdown.')
    print('6) Copy the ' + conference + '-pcconflicts.csv file downloaded this way to this directory.')

def describe_how_to_get_pcinfo(conference, file_name):
    print('Could not find a file in the current directory named ' + file_name)
    print('To get this file, do the following:')
    print('1) Visit https://' + conference + '.usenix.hotcrp.com/users?t=pc (the domain might be different for a non-USENIX conference).')
    print('2) Scroll to the bottom of the page.')
    print('3) Look for "Select people (or select all X)" and click "select all X".')
    print('4) To the right of that, after "Download", select "PC info" from the dropdown menu.')
    print('5) Click the "Go" button to the right of that dropdown.')
    print('6) Copy the ' + conference + '-pcinfo.csv file downloaded this way to this directory.')

def my_hash(s):
    """implementation of FNV-1a algorithm"""
    # https://softwareengineering.stackexchange.com/questions/49550/which-hashing-algorithm-is-best-for-uniqueness-and-speed
    # http://www.isthe.com/chongo/tech/comp/fnv/index.html#FNV-param
    h = 2166136261
    for c in s:
        h = h ^ ord(c)
        h = (h * 16777619) % (2**32)
    return h

name_stopwords = set(["da", "de", "der", "van", "von"])

institution_stopwords = set(["academy", "advanced", "america", "and", "artificial",
                             "center", "china", "chinese", "city", "computer", "computing", "department",
                             "east", "federal", "for", "foreign", "general",
                             "inc", "india", "indian", "information",
                             "inst", "institute", "instituto", "intelligence", "lab", "laboratory", "labs",
                             "limited", "llc", "ltd", "media", "national",
                             "network", "networking", "networks", "new", "north",
                             "politehnica", "polytechnic", "quantum", "research",
                             "school", "science", "sciences", "south", "state", "states", "studies",
                             "supercomputing", "superior", "tech", "technology", "technologies", "the",
                             "united", "universidade", "university", "west"])

institution_expansions = {
    'att' : ['at&t'],
    'cmu' : ['carnegie', 'mellon'],
    'iit' : ['delhi'],
    'mass' : ['massachusetts'],
    'msr' : ['microsoft'],
    'mit' : ['massachusetts'],
    'mpi' : ['planck'],
    'nyu' : ['york'],
    'penn' : ['pennsylvania'],
    'ucb' : ['berkeley'],
    'ucla' : ['angeles'],
    'ucsd' : ['diego'],
    'uconn' : ['connecticut'],
    'uw' : ['washington'],
    }

def string_to_match_set(input, type):
    stopwords = set()
    expansions = {}
    min_len = 3
    if type == 'name':
        stopwords = name_stopwords
        min_len = 2 # For names like "Li"
    elif type == 'institution':
        expansions = institution_expansions
        stopwords = institution_stopwords

    words = set([word.lower() for word in re.findall("[A-Za-z\&]+", input) if len(word) >= min_len])
    words = words.difference(stopwords)

    for shorter,longers in expansions.items():
        if shorter in words:
            for longer in longers:
                words.add(longer)

    if len(words) == 0 and len(input.strip()) >= min_len:
        # Some institutions are composed entirely of stopwords, like
        # "University of Chinese Academy of Sciences".  So if we wind
        # up with nothing, include the entirety of the input string.
        words = { input.strip().lower() }

    return words

def strings_to_match_set(inputs, type):
    return set([s for input in inputs for s in string_to_match_set(input, type)])

class PaperAuthor:
    def __init__(self, paper_num, first, last, affiliation):
        self.paper_num = paper_num
        self.first = first
        self.last = last
        self.first_last = first + " " + last
        self.affiliation = affiliation
        self.name_match_set = string_to_match_set(self.last, 'name')
        self.affiliation_match_set = string_to_match_set(self.affiliation, 'institution')

    def add_extra_affiliation(self, extra_affiliation):
        match_set = string_to_match_set(extra_affiliation, 'institution')
        self.affiliation_match_set.update(match_set)

    def __repr__(self):
        return repr(tuple([self.paper_num, self.first_last, self.affiliation]))

class PaperConflict:
    def __init__(self, paper_num, email, conflict_type):
        self.paper_num = paper_num
        self.email = email
        self.conflict_type = conflict_type
        self.solid_explanations = set()
        self.possible_explanations = set()

    def add_solid_explanation(self, explanation):
        self.solid_explanations.add(explanation)

    def add_possible_explanation(self, explanation):
        self.possible_explanations.add(explanation)

    def has_solid_explanation(self):
        return len(self.solid_explanations) > 0

    def get_all_explanations(self):
        return self.solid_explanations.union(self.possible_explanations)

    def __repr__(self):
        return repr(tuple([self.paper_num, self.email, self.conflict_type]))

class PCMember:
    def __init__(self, first, last, email, affiliation, collaborators):
        self.first = first
        self.last = last
        self.first_last = first + " " + last
        self.email = email
        self.affiliation = affiliation
        self.collaborators = collaborators
        collab_lines = collaborators.split("\n")
        self.conflict_individuals = set()
        self.conflict_institutions = set()
        self.conflict_institutions.add(self.affiliation)
        for collab_line in collab_lines:
            if collab_line.strip() == "":
                continue
            m = re.search("([^(]*)(\((.*)\))?", collab_line)
            name = m.groups()[0].strip()
            if name == "All":
                if len(m.groups()) > 2:
                    institution = m.groups()[2]
                    self.conflict_institutions.add(institution)
            else:
                self.conflict_individuals.add(name)

        self.conflict_individuals_match_set = strings_to_match_set(self.conflict_individuals, 'name')
        self.conflict_institutions_match_set = strings_to_match_set(self.conflict_institutions, 'institution')

    def match_author(self, author_match_set):
        return self.conflict_individuals_match_set.intersection(author_match_set)

    def match_institution(self, institution_match_set):
        return self.conflict_institutions_match_set.intersection(institution_match_set)

    def __repr__(self):
        return repr(tuple([self.first_last, self.affiliation, self.collaborators.replace("\n", " ")[:20]]))


class ConflictsFinder:
    def __init__(self, conference, hash_salt):
        self.conference = conference
        self.hash_salt = hash_salt

    def run(self):
        self.parse_extra_affiliations_file()
        self.parse_authors_file()
        self.parse_pcconflicts_file()
        self.parse_pcinfo_file()
        self.create_indices()
        self.find_multipaper_conflicts()
        self.explain_conflicts()
        self.generate_result_file()

    def create_indices(self):
        self.pc_index = dict([(pcmember.email, pcmember) for pcmember in self.pcmembers])
        self.author_index = defaultdict(list)
        for paper_author in self.paper_authors:
            self.author_index[paper_author.paper_num].append(paper_author)

    def parse_extra_affiliations_file(self):
        self.extra_affiliations = {}
        infile_name = self.conference + "-extraaffiliations.csv"
        if not os.path.exists(infile_name):
            print("No file %s found, so assuming no extra author affiliations beyond those in HotCRP" % infile_name)
            return

        self.extra_affiliations = defaultdict(list)
        with open(infile_name, 'r') as infile:
            reader = csv.DictReader(infile, delimiter=',')
            try:
                for row in reader:
                    email = row["email"]
                    affiliation = row["affiliation"]
                    self.extra_affiliations[email].append(affiliation)
            except:
                print("Error reading %s. Please make sure the first row consists of the 17 characters 'e', 'm', 'a', 'i', 'l', ',', 'a', 'f', 'f', 'i', 'l', 'i', 'a', 't', 'i', 'o', 'n'" % (infile_name))
                sys.exit(-1)
                

    def parse_authors_file(self):
        infile_name = self.conference + "-authors.csv"
        if not os.path.exists(infile_name):
            describe_how_to_get_authors(self.conference, infile_name)
            sys.exit(-1)

        self.paper_authors = []
        with open(infile_name, 'r') as infile:
            reader = csv.DictReader(infile, delimiter=',')
            for row in reader:
                author = PaperAuthor(row["paper"], row["first"], row["last"], row["affiliation"])
                if row["email"] in self.extra_affiliations:
                    for affiliation in self.extra_affiliations[row["email"]]:
                        author.add_extra_affiliation(affiliation)
                self.paper_authors.append(author)

    def parse_pcconflicts_file(self):
        infile_name = self.conference + "-pcconflicts.csv"
        if not os.path.exists(infile_name):
            describe_how_to_get_pcconflicts(self.conference, infile_name)
            sys.exit(-1)

        self.paper_conflicts = []
        with open(infile_name, 'r') as infile:
            reader = csv.DictReader(infile, delimiter=',')
            for row in reader:
                self.paper_conflicts.append(PaperConflict(row["paper"], row["email"], row["conflicttype"]))

    def parse_pcinfo_file(self):
        infile_name = self.conference + "-pcinfo.csv"
        if not os.path.exists(infile_name):
            describe_how_to_get_pcinfo(self.conference, infile_name)
            sys.exit(-1)

        self.pcmembers = []
        with open(infile_name, 'r') as infile:
            reader = csv.DictReader(infile, delimiter=',')
            for row in reader:
                self.pcmembers.append(PCMember(row["first"], row["last"], row["email"], row["affiliation"], row["collaborators"]))

    def find_multipaper_conflicts(self):
        # map pcmember to author that conflicts to set of papers for which that
        # author conflicts
        pcmember_to_author_to_papers = defaultdict(lambda: defaultdict(list))
        for conflict in self.paper_conflicts:
            for conflict_author in self.author_index[conflict.paper_num]:
                author_name = conflict_author.first_last
                pcmember_to_author_to_papers[conflict.email][author_name].append(conflict)

        # create a map from pcmember to set of authors each of whom conflicts with that pcmember
        # on at least two papers
        self.multiply_conflicted_authors_of_pcmember = defaultdict(set)
        for pcmember,author_map in pcmember_to_author_to_papers.items():
            for author,conflict_list in author_map.items():
                conflicting_papers = set([conflict.paper_num for conflict in conflict_list])
                if len(conflicting_papers) >= 2:
                    self.multiply_conflicted_authors_of_pcmember[pcmember].add(author)

    def check_one(self, conflict):
        # conflict.paper_num says one if its authors conflicts with conflict.email
        if conflict.email not in self.pc_index:
            conflict.add_solid_explanation("not_on_pc(%s)" % (conflict.email))
            return
        pcmember = self.pc_index[conflict.email]
        # so there's either an institutional or collaborator conflict betwixt pcmember
        # and one of the n authors of the paper.
        for paper_author in self.author_index[conflict.paper_num]:
            author_explanations = pcmember.match_author(paper_author.name_match_set)
            for author_explanation in author_explanations:
                conflict.add_solid_explanation("collaboration(%s)" % author_explanation)

            affiliation_explanations = pcmember.match_institution(paper_author.affiliation_match_set)
            for affiliation_explanation in affiliation_explanations:
                conflict.add_solid_explanation("affiliation(%s)" % affiliation_explanation)

            if pcmember.email in self.multiply_conflicted_authors_of_pcmember:
                if paper_author.first_last in self.multiply_conflicted_authors_of_pcmember[pcmember.email]:
                    conflict.add_possible_explanation("multipleconflicts(%s)" % (paper_author.first_last))

    def explain_conflicts(self):
        for conflict in self.paper_conflicts:
            self.check_one(conflict)

    def generate_result_file(self):
        unexplained_outfile_name = self.conference + "-unexplainedconflicts.csv"
        explained_outfile_name = self.conference + "-explainedconflicts.csv"
        with open(unexplained_outfile_name, 'w') as unexplained_outfile:
            with open(explained_outfile_name, 'w') as explained_outfile:
                field_names = ["paper", "email", "uid", "conflicttype", "explanations"]
                unexplained_writer = csv.DictWriter(unexplained_outfile, delimiter=',', fieldnames=field_names)
                explained_writer = csv.DictWriter(explained_outfile, delimiter=',', fieldnames=field_names)
                unexplained_writer.writeheader()
                explained_writer.writeheader()
                for conflict in self.paper_conflicts:
                    explanations = ';'.join(conflict.get_all_explanations())
                    s = "%s:%s:%s" % (self.hash_salt, conflict.email, conflict.paper_num)
                    uid = my_hash(s)
                    if conflict.has_solid_explanation():
                        explained_writer.writerow({"paper" : conflict.paper_num, "email" : conflict.email, "uid" : uid,
                                                   "conflicttype" : conflict.conflict_type, "explanations" : explanations})
                    else:
                        unexplained_writer.writerow({"paper" : conflict.paper_num, "email" : conflict.email, "uid" : uid,
                                                     "conflicttype" : conflict.conflict_type, "explanations" : explanations})

args = parser.parse_args()
if not args.conference:
    print("ERROR:  Missing --conference parameter\n")
    parser.print_help()
    sys.exit(-1)

if not args.hash_salt:
    print("ERROR:  Missing --hash-salt parameter\n")
    parser.print_help()
    sys.exit(-1)

finder = ConflictsFinder(args.conference, args.hash_salt)
finder.run()
