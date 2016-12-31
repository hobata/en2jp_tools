#!/usr/bin/python
# -*- coding: utf-8 -*- 
# Document for 3gpp TS xxx.xx
#
import sys
import ezodf
import re
import numpy as np
from ezodf import Paragraph
from ezodf import Hyperlink
from ezodf.xmlns import CN
from ezodf.body import AnnotationBody #add new class

def print_help():
  print "This program needs one parameter."
  print "Usage:"
  print " python odfxx.py [filename]"
  print "Parameter:"
  print " filename: source filename"
  print " ex. 36300-d40.odt"
  print "output file ex. cmt_36300-d40.odt\n"

# MAIN
# search string for find top, delimita
dicList = np.array([[ 'a reference to a 3GPP document (including a GSM document)', '\t'], \
[ 'For the purposes of the present document, the following terms and definitions', ':'] , \
[ 'For the purposes of the present document, the abbreviations', '\t' ]])

#dictionary list
dict = {}

argvs = sys.argv  # list of command line
argc = len(argvs) # prameter number

if argc != 2:
  print_help()
  sys.exit()

#open odt file
doc = ezodf.opendoc(argvs[1])
if doc.doctype != 'odt':
  print 'not odt document type. exit..'
  sys.exit()

print doc.meta
print 'This document has', len(doc.body), 'elements'

# make dictionary
def make_dic(flag, str):
  if flag == 1:
    if dicList[0][1] in str:
      tmp = str.split(dicList[0][1]) #separate word and description
      if len(tmp) >= 2:
        tmp[1] = tmp[1].replace(' – ', '_') #exception fix: append_text
        dict[tmp[0]] = tmp[1]
      else:
        print tmp
      return flag
    else:
      flag = 2 #proceed to enter 3
  if flag == 3:
    if dicList[1][1] in str: 
      tmp = str.split(dicList[1][1]) #separate word and description
      if len(tmp) >= 2:
        tmp[1] = tmp[1].replace(' – ', '_') #exception fix: append_text
        dict[tmp[0]] = tmp[1]
      else:
        print tmp
    else:
      flag = 4 #proceed to enter 5
  if flag == 5:
    if dicList[2][1] in str: 
      tmp = str.split(dicList[2][1]) #separate word and description
      if len(tmp) >= 2:
        tmp[1] = tmp[1].replace(' – ', '_') #exception fix: append_text
        dict[tmp[0]] = tmp[1]
      else:
        print tmp
    else:
      flag = 6
    return flag
  if dicList[0][0] in str:
    return 1
  if dicList[1][0] in str:
    return 3
  if dicList[2][0] in str:
    return 5
  return flag

def rfc_num(str):
  str = str.replace('.', ' ')
  str = str.replace(':', ' ')
  tmp = str.split(' ')
  if len(tmp) >= 3:
    try:
      n = int(tmp[2])
    except:
      print 'rfc_num:exception:' + str
      n = 0
    finally:
      pass
  else:
    n = 0
  return n

def ts_num(str):
  str1 = str.replace('.', ' ')
  str2 = re.sub(r'[^\s\w]+', ' ', str1) #replace irregular char to space
  tmp = str2.split()
  if len(tmp) >= 4:
    try:
      n = int(tmp[2])
      m = int(tmp[3])
    except:
      print 'ts_num:exception:' + str2
      print 'tmp:', tmp 
      n = 0
      m = 0
    finally:
      pass
  else:
    n = 0
    m = 0
  return n, m

def append_str(obj, tmp):
  try:
    #add key word description after text
    obj.append_text(tmp)
  except:
    print 'append_str:exception:' + tmp

# MAIN ROUTINE
# make dictionary
paragraphs = doc.body.findall(CN('text:p'))
print "Making dictionary"
flag = 0
count = 0
i = 0
for obj in paragraphs:
  str = obj.plaintext().encode('utf-8')
  print i, ' ' + str 
  i += 1
  if flag < 6:
    flag = make_dic(flag, str)
    continue
  elif flag == 6:
    print 'Add annotion'
    flag = 7 
  str = str.replace(')', ' ') #clean separation charactor
  str = str.replace('.', ' ') #same as above
  str = str.replace(',', ' ') #same as above(new)
  tmp = str.split()  # get word
  tmp2 = sorted(set(tmp), key=tmp.index) #delete duplicate word
  for wd in tmp2:
    if wd in dict:
      count += 1
      obj.append_text(u'\n') #add return before annotation line
      if wd.find('[') > -1: #reference link
        hlink = Hyperlink()
        tmp = ''
        if dict[wd].find('RFC') > -1:
          n = rfc_num(dict[wd]) #get rfc number
          if n == 0: #can not find RFC number
            tmp = '[' + wd + '] ' + dict[wd]
            print "Can not find RFC number " + tmp
            append_str(obj, tmp)
            continue
          tmp = 'http://www.ietf.org/rfc/rfc{0}.txt'.format(n)
        elif dict[wd].find('TS') > -1:
          n, m = ts_num(dict[wd]) #get ts number
          if n == 0 and m == 0: #can not find TS number
            tmp = '[' + wd + '] ' + dict[wd]
            append_str(obj, tmp)
            continue
          tmp = 'http://www.3gpp.org/ftp/Specs/archive/{0}_series/{0}.{1:03d}'.format(n, m)
        elif dict[wd].find('IEEE') > -1:
          tmp = 'http://standards.ieee.org/getieee802/download/802.11-2012.pdf'
        hlink.href = tmp
        hstr = wd
        try:
          hlink.text = hstr
          obj.append(hlink)
          tmp = re.sub(r'[^\s\w;]+', ' ', dict[wd]) #replace irregular char to space
          obj.append_text(':' + tmp)
        except:
          print 'for:exception:' + hstr + ':' + dict[wd]
          print 'dict:', dict[wd]
        finally:
          pass
      else:
        tmp = '[' + wd + '] ' + dict[wd]
        append_str(obj, tmp)

#test
#        obj.text= '123'

#        try:
#          #add key word description after text
#          obj.append_text(tmp)
#        except:
#          print 'exception:' + tmp
#        finally:
#          pass
print dict

print 'read dictionary', count, 'times'
print 'store new file'
tmp ='cmt_' + argvs[1]
doc.saveas(tmp)
sys.exit()


#BACKUP
#OK  doc.body.append(Paragraph('Add 1st text paragraph.'))

# convert file
print "Add annotation"
paragraphs = doc.body.findall(CN('text:p'))
i = 0
for obj in paragraphs:
#NG    obj.append(anno)
  obj2 = Paragraph('Anno')
  obj.append(obj2)

  obj.append_text(":" + str(i))
  print str(i) + ":" + obj.plaintext().encode('utf-8')
  i += 1
#save
doc.saveas('cnv_' + argvs[1])
