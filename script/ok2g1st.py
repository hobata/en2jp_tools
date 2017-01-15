# okular export txt to google translate
# -*- coding: utf-8 -*-

import os, sys, re, time

def print_help():
  print "This program needs one parameter."
  print "Usage:"
  print " get temporary txt : python ok2g1st.py f_name1 > temparary_file"
  print " get target file   : python ok2g2nd.py temporary_file  > target_file"
  print "Parameter:"
  print " f_name1: okular exported txt file name"
  print "temporary file: line head indicators:"
  print " d: delete line"
  print " n: no action"
  print " c: connect to fllowing line"
  print " t: line of table"

# replace list
replace_list = [ ["Copyright © 2012 IEEE. All rights reserved","PAGE"], ]

# delete line string
del_line = [ "METROPOLITAN", "WIRELESS LAN MAC AND PHY SPECIFICATIONS" ]
entire_line = "IEEE"

# match pattern
ptn_h = r"  [-a-z0-9A-Z(]" # table
re_h = re.compile(ptn_h)
ptn_cla = r" {0,1}[1-9A-Z][\.1-9]" # clause
re_cla = re.compile(ptn_cla)

tbl_col = []
def chkConRow(mlist):
  global tbl_col
  if len(tbl_col) >= len(mlist):
    for m in mlist:
      if m in tbl_col:
        tbl_col = mlist
        return True # continue row
  tbl_col = mlist
  return False # new row

strDic = {}
def makeTableRaw(r):
  global strDic
  strRaw = ""
  mlist = []
  iter = re_h.finditer(r)
  for m in iter:
    mlist.append(m.start())
  retCont = chkConRow(mlist)
  if retCont:
    for i, m in enumerate(mlist): # append string
      if m in strDic:
        if m == mlist[-1]: # last item
          strDic[m] = strDic[m] + " " + r[m+2:] # tail
          strDic[m] = strDic[m].replace("\n", "")
        else:
          # a head of next
          strDic[m] = strDic[m] + " " + r[m+2:mlist[i+1]].strip()
  else:
    # print row
    for k, v in sorted(strDic.items()): # sort by key
      strRaw = strRaw + "\n" + v.strip()
    # new row
    strDic = {}
    for i, m in enumerate(mlist):
      if m == mlist[-1]: # last item
        strDic[m] = r[m+2:] # tail
        strDic[m] = strDic[m].replace("\n", "") # tail
      else:
        strDic[m] = r[m+2:mlist[i+1]].strip() # a head of next

  return len(mlist), retCont, strRaw

# MAIN
argvs = sys.argv  # list of command line
argc = len(argvs) # prameter number

if not argc == 2:
  print_help()
  sys.exit()

fn = argvs[1]
if not os.path.exists(fn):
  print "no source file"
  sys.exit()

#open files
infile = open(fn, "r")
read_lines = infile.readlines()
infile.close()

# store status area
lineStatus = [""] * len(read_lines) # each line status
tableRaw = [""] * len(read_lines) # table raw strings
for i, r in enumerate(read_lines):
  r = r.replace("—", "-") # force replace
  flag = 0 # for replace_list
  for s in replace_list:
    if s[0] in r:
      lineStatus[i] = "r" # replace line
      flag = 1
      break
  if flag == 1:
    continue
  flag = 0 # for del_line
  for s in del_line:
    if s in r:
      lineStatus[i] = "d" # delete line
      flag = 1
      break
  if flag == 1:
    continue
  if entire_line == r.strip(): # entire line match
    lineStatus[i] = "d" # delete line
    continue
  if "..." in r:
    lineStatus[i] = "n" # table of contents
    continue
  if re_cla.match(r):
    lineStatus[i] = "n" # clause
    continue
  if r[:2] == "  ": # may be table
    col, newRow, strRaw  = makeTableRaw(r)
    if col == 0: # no row
      lineStatus[i] = "n"
      continue
    if not strRaw == "":
      tableRaw[i] = strRaw
    if i == 0:
      prev = "n" # 1st line
    else:
      prev = lineStatus[i-1][0]
    if (not prev == "t") and col == 1:
      lineStatus[i] = "n" # 1st line of table is not "t1"
      continue
    lineStatus[i] = "t%d%s" % (col, str(newRow)[0]) # in table
    continue
  else:
    lineStatus[i] = "c" # normal line
  if len(r) < 70 or r[-2] == "." or r[-2] == ":":
    lineStatus[i] = "n" # no action
    continue

for i, s in enumerate(lineStatus):
  if not s[0] == "t":
    print s[0] + "__:" + read_lines[i].replace("\n", "")
  else:
    print s[:3] + ":" + read_lines[i].replace("\n", "")
