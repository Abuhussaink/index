import argparse
import os
import sys
import requests
from PyPDF2 import PdfReader

# Parse input
usage = """{}SANS Txt to Index
Use PyPDF2 to convert a SANS PDF to a txt file, then generate its index here.
Usage:
\t-i, --input-file: PDF file of SANS book.
\t-o, --output-file: file to save the new index.
\t-n, --student-name: full name of the student, used to split pages by delimiter.
"""

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input-file", help="PDF file of SANS book.")
parser.add_argument("-o", "--output-file", help="output file of the index.")
parser.add_argument("-n", "--student-name", help="full name of the student.")
options = parser.parse_args(sys.argv[1:])

if not options.input_file:
    exit(usage.format("Please enter a PDF file.\n"))

if not options.output_file:
    input_dir, input_filename = os.path.split(options.input_file)
    output_filename = os.path.splitext(input_filename)[0] + ".txt"
    options.output_file = os.path.join(input_dir, output_filename)

delimiter = "Licensed To: "
if options.student_name:
    delimiter += options.student_name

# Get common English words
common_words = requests.get("https://raw.githubusercontent.com/dwyl/english-words/master/words.txt").text.split("\n")

# Function to recursively strip given characters in a word
characters_to_strip = "()'\":,”“‘?;-•’—…[]!"
phrases_to_strip = ["'s", "'re", "'ve", "'t", "[0]", "[1]", "[2]", "[3]", "[4]", "[5]", "[6]"]


def strip_characters(word):
    word_length = len(word)
    word = word.replace("’", "'")
    while True:
        for phrase in phrases_to_strip:
            if word.endswith(phrase):
                word = word[:len(phrase)]
        word = word.strip(characters_to_strip).rstrip(".")
        if len(word) == word_length:
            return word
        else:
            word_length = len(word)


# Check if a word should be added to the index
def word_is_eligible(word):
    # Length check
    if len(word) < 3:
        return False
    # Starts with a number
    if word[0].isdigit():
        return False
    # Not a common English word
    if word.lower() in common_words or word.lower() + "s" in common_words:
        return False
    # Not a SANS URL
    if word.startswith("http://") or word.startswith("https://"):
        return False
    return True


# Get pages from PDF
with open(options.input_file, "rb") as f:
    pdf_reader = PdfReader(f)
    num_pages = len(pdf_reader.pages)
    pages = [pdf_reader.pages[page_num].extract_text() for page_num in range(num_pages)]

# Get words per page
index = {}  # Stores page number and words on page
total_words = []  # Stores all words encountered
for page_idx, page in enumerate(pages):
    # Recursively replace whitespace with a single space
    page = page.replace("\n", " ").replace("\t", " ")
    page_len = len(page)
    while True:
        page = page.replace("  ", " ")
        if len(page) == page_len:
            break
        else:
            page_len = len(page)
    # Trim whitespace
    page = page.strip()
    # Get words
    words = page.split(" ")
    long_words = []
    for word in words:
        # Strip some punctuation
        word = strip_characters(word).lower()
        # If the threshold is met, append to the index
        if word_is_eligible(word):
            total_words.append(word)
            long_words.append(word)
    index[page_idx] = long_words

# Get result strings
results = []
for word in set(total_words):
    pages_word_is_in = []
    # Get page numbers
    for page in index.keys():
        if word in index[page]:
            pages_word_is_in.append(str(page))

    if len(pages_word_is_in) < 15:
        joined_pagenums = ', '.join(pages_word_is_in)
        # Only append if not a page number
        if word != joined_pagenums:
            results.append(f"{word}: {', '.join(pages_word_is_in)}")

# Sort output
results.sort(key=str.casefold)

# Save index to output file
with open(options.output_file, "w", encoding="utf-8") as output_file:
    output_file.write("\n".join(results))

print(f"Index generated and saved to {options.output_file}")