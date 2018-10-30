# Use this file to output generated HTML to output_html.txt

import generate_html_methods
import os
import sys


html = generate_html_methods.openraw ('input_html.txt') # reads the input_html.txt file
toc = generate_html_methods.generate_TOC (html) # generates the table of contents with links
body = generate_html_methods.generate_HTML (generate_html_methods.listify(generate_html_methods.linkify(html))) # generates the body text compelete with links

# Used to create output into a text file if needed
totalHtml = toc + body
generate_html_methods.process_html (totalHtml, 'output_html.txt')