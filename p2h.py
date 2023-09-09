#!/usr/bin/python3

__version__ = "2023-09-09"
__author__ = "Eric Light / Rhyven"
__credits__ = "Credit to Anthony Nelzin for his Pelican-to-Hugo migration script - https://github.com/anthonynelzin/PelicanToHugo/ - it gave me a head-start on some approaches."


"""
Convert Markdown files using Pelican-style front matter, into the strict YAML front matter required by Hugo and similar static site generators.

usage: p2h.py inputlocation [outputlocation]

  python3 p2h.py ./Pelican/mysite/content/
  python3 p2h.py ./Pelican/mysite/content/category/mypost.md

By default, the converted file will go to STDOUT. You can redirect this to a flie with standard redirects, or you can provide an output location:

  python3 p2h.py ./Pelican/mysite/content/ ./Hugo/mysite/content/
  python3 p2h.py ./Pelican/mysite/content/category/mypost.md ./Hugo/mysite/content/category/mypost.md
"""


def process_Pelican_content(pelican_text, input_file_name="", input_file_date=None):
  """ Takes Pelican-type text input and returns the same text with a full YAML front matter.
  Optionally can receive a name and last-modified date, which can be used to infer missing data."""

  if args.debug: print("Entered processor; first line of the input file reads: %s" % pelican_text[0])
  converted_text = []
  head_lineno = 0

  # Find the first empty line break, but ignore it if the blank line is the first line
  for file_line in pelican_text:
    if file_line.isspace():
      if head_lineno > 1: break
    head_lineno+=1
  if args.debug: print("Blank line discovered at line %s; assuming all front matter will exist in prior lines." % head_lineno)

  # We don't know what order people will actually create their front matter, so need to run over everything in the first block
  # Use re.match instead of re.search, because we only want results from the front of a line.
  # Use filter so we can pass the regex over the entire list of the front matter block without iterating manually

  frontmatter = {}
  for variable_name in ["title", "author", "date", "summary", "modified", "category", "slug", "tags"]:
    try:
      # regex match for front matter (i.e., title) in the head of the file, return anything after the colon, strip whitespace & newlines
      frontmatter.update({variable_name: list(filter(compile("\s*"+variable_name+"?:", IGNORECASE).match, file_contents[:head_lineno]))[0].split(' ', 1)[1].strip()})

      '''
      trying to explain this regex above, using 'title' as the example. From inside out:

      * file_contents[:head_lineno] --- only bother looking through the top section of the file (until the first blank line)
      * .match --- match requires results to be at the front of the line (i.e., you can use the word 'Title' in your title)
      * compile("\s*"+variable_name+"?:", IGNORECASE) --- case-insensitive regex for 'title:', possibly indented, maybe with a space before the colon
      * filter( ... ) --- turn the regex result into something iterable, so we can treat it as a list
      * list( ... )[0].split(' ', 1)[1].strip() --- convert regex result into a list; take the part after 'title:', strip whitespace and newlines
      * frontmatter.update({variable_name: ... }) --- add the discovered item to the dict, into a key named 'title'

      '''

    except IndexError:
      # If one of the front matter types wasn't used, don't worry about it
      pass

  # Colons in titles don't fly with Hugo; if a title has any, replace them with a hyphen
  frontmatter.update({'title': frontmatter.get('title').replace(':','-')})

  if args.debug: print("Discovered the following front matter: %s" % frontmatter)
  if args.debug: print("Attemping to automatically complete any missing title, category, or date...")

  # Attempt to complete missing front matter; title from the filename, category from the parent folder name, and date from last-modified
  if frontmatter.get('category') is None: frontmatter.update({'category': path.split(path.split(input_file_name)[0])[1]})
  if frontmatter.get('date') is None: frontmatter.update({'date': input_file_date})
  if frontmatter.get('title') is None:
    # I really hope this branch never gets hit, because this is stupid
    frontmatter.update({'title': path.split(input_file_name)[1]})
    print("Had to kludge in a title for %s; you should probably manually edit this one." % input_file_name)
  if args.debug: print("Discovered the following front matter: %s" % frontmatter)

  # Start constructing output
  converted_text.append("---\n")

  # Pop the majority of the front matter out onto the converted_text
  for variable_name in ["title", "author", "summary", "category", "slug"]:
    if not frontmatter.get(variable_name) is None:
      converted_text.append("%s: %s\n" % (variable_name, frontmatter.pop(variable_name)))

  # Whatever the input date format was, try to output it as iso8601, because I'm opinionated
  converted_text.append("date: %s\n" % parser.parse(frontmatter.get('date')).isoformat())
  if not frontmatter.get('modified') is None: converted_text.append("modified: %s\n" % parser.parse(frontmatter.get('modified')).isoformat())

  # Do the tags:
  if not frontmatter.get('tags') is None:
    converted_text.append("tags:\n")
    for tag in frontmatter.pop('tags').split(","):
      converted_text.append(" - %s\n" % tag.strip())

  converted_text.append("---\n")

  if args.debug:
    print("Converted front matter reads:\n-----------------------")
    print(*converted_text)

  # That's it! The front matter is finished! Onwards to the rest of it!
  # Read the rest of the input data, skipping the header; strip trailing whitespace, leave leading indents
  for file_line in pelican_text[head_lineno:]:
    converted_text.append(file_line)

  return converted_text


# Check & parse launch arguments; return error if no arguments given
import argparse
argparser=argparse.ArgumentParser(description="Convert Markdown files from Pelican's front matter syntax, to the strict YAML frontmatter syntax that Hugo and other static engines expect.")
argparser.add_argument("input_location", help="Your source Pelican data. This can be either a single file, or a path containing multiple files.")
argparser.add_argument("output_location", nargs="?", help="The path to output processed data. By default, data will be output to STDOUT.", default=False)
argparser.add_argument("-d", "--debug", help="Debug/verbose mode", action="store_true")
argparser.add_argument("-o", "--overwrite", help="Overwrite existing files (default is to skip)", action="store_true")
args=argparser.parse_args()
if args.debug: print("Arguments given: %s" % args)


# Make sure the given input exists, and determine whether it's a file or a directory
from os import path
if not path.exists(args.input_location):
  if args.debug:
    import errno
    from os import strerror
    raise FileNotFoundError(errno.ENOENT, strerror(errno.ENOENT), args.input_location)
  else:
    print("%s: No such file or directory" % args.input_location)
    exit()

files_to_process = []

# Single file mode
if path.isfile(args.input_location):
  if args.debug: print("%s is an existing file; operating in single-file mode." % args.input_location)
  files_to_process = [args.input_location]
  if args.debug: print("Single file to process: %s" % files_to_process)

# Whole folder mode
elif path.isdir(args.input_location):
  if args.debug: print("%s is an existing folder location; traversing..." % args.input_location)
  from os import listdir

  # Empty folder
  if len(listdir(args.input_location)) == 0:
    print("No files found in %s, nothing to do!" % args.input_location)
    exit()

  # Iterate through list of candidate files, only process those that seem sensible.
  # potential_target must: not start with a dot, finish with .md, and must be a file
  if args.debug: print("Path contents: %s" % listdir(args.input_location))
  for potential_target in listdir(args.input_location):
    if not path.isfile(path.join(args.input_location, potential_target)):
      if args.debug: print("%s is not a file; skipping." % potential_target)
      continue
    if potential_target.startswith("."):
      if args.debug: print("%s is a dotfile; skipping." % potential_target)
      print("Skipping %s as it is a dotfile." % potential_target)
      continue
    if potential_target.endswith(".md"):
      if args.debug: print("%s has a .md extension; adding to list." % potential_target)
      files_to_process.append(path.join(args.input_location, potential_target))
    else: print("Skipping %s as it does not have the .md extension." % potential_target)


# We have a reasonably valid list of files, time to start iterating and sending them to the processor
from datetime import datetime
from dateutil import parser
from re import sub, match, compile, IGNORECASE

if args.debug: print("List of files to process is now: %s" % files_to_process)
for target_file in files_to_process:
  if args.debug: print("Opening %s for input..." % target_file)
  with open(target_file) as input_file:
    file_contents = input_file.readlines()
  if args.debug: print("Calling content processor with input file path (%s) and modified time (%s)." % (path.abspath(target_file), datetime.fromtimestamp(path.getmtime(target_file)).isoformat()))

  # Let's goooooooo
  hugo_text = process_Pelican_content(file_contents, path.abspath(target_file), datetime.fromtimestamp(path.getmtime(target_file)).isoformat())

  # We're back from the iterator, and hugo_text should now contain hugo-compatible files!
  if args.debug: print("Returned from Pelican processor; hugo_text is %s lines long." % len(hugo_text))

  if args.output_location:
    # We've been asked to output our files to a destination
    output_fullpath = path.join(args.output_location, path.split(target_file)[1])
    if not path.exists(args.output_location):
      print("Output path %s doesn't exist; creating it." % args.output_location)
      from os import makedirs
      makedirs(args.output_location)

    if args.debug: print("Outputting processed data to %s." % output_fullpath)
    try:
      # Default to writing in 'x' mode, meaning it will not overwrite existing files
      filemode='x'
      if args.overwrite: filemode='w'
      with open(output_fullpath, filemode) as hugo_file:
        hugo_file.writelines(hugo_text)
    except FileExistsError:
      print("An output file already existed at %s; skipping." % output_fullpath)

  else:
    # Outputting to screen
    print(*hugo_text, sep='\n')
