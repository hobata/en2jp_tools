# PDF annotation converter
# -*- coding: utf-8 -*-

import os, sys, re, time

#Location
#/usr/local/lib/python2.7/dist-packages/PyPDF2/pdf.py
from PyPDF2 import PdfFileWriter, PdfFileReader, PdfFileMerger

def get_contents_pdftk(pdfName):
  outName = "out.tmp"
  os.system("pdftk %s dump_data | grep BookmarkTitle | cut -d ':' -f 2 | sed -e 's/^ *//' > %s" % (pdfName, outName))
  fd = open(outName)
  ret_list = fd.readlines()
  fd.close()
  os.system("rm -rf %s" % (outName))
  #print ret_list
  sList = []
  for s in ret_list: #separate number and description
    s = s.replace('\n', '')
    sList.append(s.split(' ', 1)) # maxsplit=1
  print sList
  return sList

def print_help():
  print "This program needs one parameter."
  print "Usage:"
  print " python dumpxx.py [filename]"
  print "Parameter:"
  print " filename: source filename"
  print "ex. 1000.pdf"
  print "output file ex. 1000.pdf > pdf.txt\n"

def remove_header(s):
  iptn = r"^IEEE.*reserved\." #page header and footer
  s = re.sub(iptn , '', s)
  return s.strip()

def only_ascii(tmp):
  s = ""
  for i in range(0, len(tmp)-1):
    if tmp[i] <= '~': #is ascii character
      s += str(tmp[i])
    else:
      s += ' ' #replace character 
  return s

##### MAIN ####
start_time = time.time()

#check parameter
argvs = sys.argv  # list of command line
argc = len(argvs) # prameter number
if argc != 2:
  print_help()
  sys.exit()

print 'Get raw data'
input1 = PdfFileReader(open(argvs[1], "rb"))
pageObj = input1.getPage(0)

# print how many pages input1 has:
num_page = input1.getNumPages()
print "source pdf file has %d pages." % num_page

pg_txt = []
one_txt = ""
raw_txt = ""
print "Get Document txt" 
for var in range(0, num_page - 1):
#  print 'processing page:' + str(var + 1) 
  pageObj = input1.getPage(var)
  pdf_txt = ""
  try:
    pdf_txt = pageObj.extractText()
  except:
    pg_txt.append(pdf_txt)
    continue
  pdf_txt = pdf_txt.encode('utf-8')
#conversion to get plain strings
  tmp = pdf_txt
  raw_txt += tmp
  tmp = tmp.replace('\n', '')
  tmp = remove_header(tmp)
  tmp = only_ascii(tmp)
  pg_txt.append(tmp)
  one_txt += tmp

#open input file and get width and height
print 'Get contents'
cnt_list = get_contents_pdftk(argvs[1])
#print cnt_list

#insert line feed
p = r"[a-z)0-9A-Z]\. [A-Z]" #find end of line
ptn = re.compile(p)
pg_txt2 = []
for i, tmp in enumerate(pg_txt):
  iter = re.finditer(ptn, tmp)
  tmpE = tmp
  for match in iter:
    # replace ' ' to '\n'
    tmpE = tmpE[:match.start()+2] + '\n' + tmpE[match.end()-1:]
  for cnt in cnt_list:
    if len(cnt) >= 2:
      tmp2 = cnt[0] + ' ' + cnt[1]
      tmpE = tmpE.replace(cnt[0] + cnt[1], tmp2, 1)
      tmpE = tmpE.replace(tmp2, '\n' + tmp2 + '\n', 1)
    elif len(cnt) == 1:
      tmpE = tmpE.replace(cnt[0], '\n' + cnt[0] + '\n', 1)
  pg_txt2.append(tmpE)
  print "page " + str(i+1)
  print pg_txt2[i]
  print "\n"
"""
print "@@@@@ PAGE @@@@@" 
print pg_txt
print "@@@@@ RAW @@@@@" 
print raw_txt
print "@@@@@ ONE @@@@@" 
print one_txt
print "@@@@@ CONTENTS @@@@@" 
for st in get_contents_pdftk(argvs[1]):
  print st
"""

print time.time()-start_time
sys.exit()
