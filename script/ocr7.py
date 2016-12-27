# -*- coding: utf-8 -*-
# 

import sys, os, re, time

def print_help():
  print "This program needs one parameter."
  print "Usage:"
  print " python ocrxx.py [filename]"
  print "Parameter:"
  print " filename: source filename"
  print "ex. page-001.txt"
  print "output to stdout."

def make_line(s):
  s_list = s.split('\n')
  p = r".*[\.\:]$" #check line end
  ptn = re.compile(p)

  n_list = []
  for i, s in enumerate(s_list): #skip line
    if s.find("Copyright") >= 0 or s.find("METROPOLITAN") >=0:  
      continue
    n_list.append(s)

  n_list2 = []
  str = ""
  for i, s in enumerate(n_list): # multiple line to one line
    if s == "" or re.match(ptn, s): #end line is ':' or '.'
      n_list2.append(str + ' ' + s)
      str = ""
    else: #end line is not ':' nor '.'
      if str ==  "":
        str = s
      else:
        str += ' ' + s
  if str != "":
    n_list2.append(str)
  str = ""
  for s in n_list2:
    str += s + '\n'
  return str

##### MAIN #####
start_time = time.time()
#check parameter
argvs = sys.argv  # list of command line
argc = len(argvs) # prameter number
if argc != 2:
  print_help()
  sys.exit()

#open file
infile = open(argvs[1], 'r')
s = infile.read()
infile.close()
#output
s1 = make_line(s)
print make_line(s1)
sys.exit()
