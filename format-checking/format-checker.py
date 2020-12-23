# format-checker.py: generate PDFs to make it easy to check formatting
#   - used for checking for obvious formatting issues
# Authors: Jon Howell <jonh@jonh.net>
#          Jay Lorch <jaylorch@gmail.com>
# Released into the public domain.

from PyPDF2 import PdfFileWriter, PdfFileReader
import argparse
import csv
import io
import re
import smtplib
import sys
import os
import zipfile

parser = argparse.ArgumentParser('format-checker', epilog="""
This script takes papers submitted to a conference and generates PDFs
that aid a chair in checking that they satisfy formatting
requirements.

It will create one document for each paper containing the 1st, nth,
and (n+1)st pages, where n is the page limit. The 1st and nth will be
overlayed with a blue stencil showing leading, while the (n+1)st will
be overlayed with a red stencil showing leading. The red color will
alert the reader to make sure it doesn't contain any content besides
things like references that are allowed to exceed the page limit.

It will also create a document all_papers_stenciled.pdf containing the
concatenation of all the above documents.

It will also create a document all_first_pages.pdf containing the
concatenation of all first pages *without* stencil overlays. This is
to help make sure no authors accidentally included author information
on the first page.

It creates all these documents with a prefix of 'output/' (i.e., in
the directory 'output'); you can override this with --output-prefix.
""")
parser.add_argument('conference', help='conference name used as a prefix of -papers.zip file name exported by HotCRP, e.g., osdi21')
parser.add_argument("--page-limit", help="page limit, default 12", default=12, type=int)
parser.add_argument("--output-prefix", help='prefix for all output files, default "output/"', default="output/", type=str)

def describe_how_to_get_papers(conference, file_name):
    print('Could not find a file in the current directory named ' + file_name)
    print('To get this file, do the following:')
    print('1) Visit https://' + conference + '.usenix.hotcrp.com/search?q=&t=act (the domain might be different for a non-USENIX conference).')
    print('2) Scroll to the bottom of the page.')
    print('3) Look for "Select papers (or select all X)" and click "select all X".')
    print('4) To the right of that, after "Download", select "Submissions" from the dropdown menu.')
    print('5) Click the "Go" button to the right of that dropdown.')
    print('6) Copy the ' + conference + '-papers.zip file downloaded this way to this directory.')

class FormatChecker:
    def __init__(self, conference, page_limit, output_prefix):
        self.conference = conference
        self.page_limit = page_limit
        self.output_prefix = output_prefix

    def run(self):
        self.ensure_directory_exists()
        self.blue_stencil_pdf = PdfFileReader(open("blue_stencil.pdf", "rb"))
        self.red_stencil_pdf = PdfFileReader(open("red_stencil.pdf", "rb"))
        self.apply_to_zip()

    def ensure_directory_exists(self):
        if re.search(r"[/\\]$", self.output_prefix):
            if not os.path.exists(self.output_prefix):
                os.mkdir(self.output_prefix)

    def apply_stencil(self, target_stream, all_papers_stenciled):
        target_pdf = PdfFileReader(target_stream)
        page_count = target_pdf.getNumPages()
        for page_num,stencil_pdf in (
            (0, self.blue_stencil_pdf),
            (self.page_limit - 1, self.blue_stencil_pdf),
            (self.page_limit, self.red_stencil_pdf)):
            if page_num >= page_count:
                continue
            input_page = target_pdf.getPage(page_num)
            input_page.mergePage(stencil_pdf.getPage(0))
            all_papers_stenciled.addPage(input_page)

    def apply_stencil_one(self, target_stream, output_name):
        output_pdf = PdfFileWriter()
        self.apply_stencil(target_stream, output_pdf)
        output_pdf.write(open(output_name, "wb"))

    def collect_first_page(self, target_stream, all_first_pages):
        target_pdf = PdfFileReader(target_stream)
        input_page = target_pdf.getPage(0)
        all_first_pages.addPage(input_page)

    def apply_to_zip(self):
        infile_name = self.conference + "-papers.zip"
        if not os.path.exists(infile_name):
            describe_how_to_get_papers(self.conference, infile_name)
            sys.exit(-1)

        zf = zipfile.ZipFile(infile_name, 'r')
        all_papers_stenciled = PdfFileWriter()
        all_first_pages = PdfFileWriter()
        for name in zf.namelist():
            mo = re.search("(\d+)\.pdf", name)
            if mo:
                nbr = int(mo.groups()[0])
                stream = io.BytesIO(zf.open(name, "r").read())
                output_file_name = self.output_prefix + name
                print("Generating %s" % (output_file_name))
                self.apply_stencil_one(stream, output_file_name)
                self.apply_stencil(stream, all_papers_stenciled)
                self.collect_first_page(stream, all_first_pages)

        output_file_name = self.output_prefix + "all_papers_stenciled.pdf"
        print("Generating aggregate %s" % (output_file_name))
        all_papers_stenciled.write(open(output_file_name, "wb"))

        output_file_name = self.output_prefix + "all_first_pages.pdf"
        print("Generating aggregate %s" % (output_file_name))
        all_first_pages.write(open(output_file_name, "wb"))


args = parser.parse_args()
checker = FormatChecker(args.conference, args.page_limit, args.output_prefix)
checker.run()
