# okular export txt to google translate
# -*- coding: utf-8 -*-

import os, sys, re, time

def print_help():
  print "This program needs one parameter."
  print "Usage:"
  print " get temporary txt : python ok2g1.py f_name1 > temparary_file"
  #print " get target file   : python ok2g2.py temporary_file  > target_file"
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
  #print mlist
  retCont = chkConRow(mlist)
  #print retCont
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
out_txt = [] # outpur raw strings
for i, r in enumerate(read_lines):
  tmp = r[4:] # out(work)_string

  if i >= 1:
    if read_lines[i-1][0]  == "t" and r[0] <> "t": # end table
      # print row
      for k, v in sorted(strDic.items()): # sort by key
        out_txt.append(v.strip() + '\n')
      # clear row
      strDic = {}

    if read_lines[i-1][0]  == "c": # connect
      out_txt[-1] = out_txt[-1][:-1] + " " + tmp # end of line is "\n"
      out_txt[-1] = out_txt[-1].replace("  ", " ")
      continue

  if r[0] == "c": # same as noaction but connect next line
    out_txt.append(tmp)
    continue

  if r[0] == "n": # no action
    out_txt.append(tmp)
    continue

  if r[0] == "d": # delete
    continue

  flag = 0
  if r[0] == "r": # replace
    for s in replace_list:
      if s[0] in r:
        tmp = tmp.replace(s[0], s[1])
        flag = 1
        break
    if flag == 1:
      out_txt.append(tmp)
      continue

  if r[0] == "t": # table
    tmp = "  " + tmp # for recognize as table
    col, newRow, strRaw  = makeTableRaw(tmp)
    if not strRaw == "":
      out_txt.append(strRaw)

for s in out_txt:
  print s
  #print s.replace('\n', '')
