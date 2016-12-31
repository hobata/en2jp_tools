#!/usr/bin/python
# -*- coding: utf-8 -*- 
# Document for IETF RFC xxx.xx
#
import sys, re, os, ezodf, random
from ezodf import Paragraph, Heading, Span, Hyperlink
from ezodf.xmlns import CN
from lxml import etree

def print_help():
  print "This program needs one parameter."
  print "Usage:"
  print " python txtxx.py [filename]"
  print "Parameter:"
  print " filename: source file name(ex. rfc3261.txt)"
  print "output file  ex. cmt_rfc3261.odt\n"

def add_comment(s, para):
  anno_no = random.randint(1, 10000) 
  #comment start
  es = etree.Element(CN("office:annotation"))
  bk = Span(xmlnode=es)
  bk.set_attr(CN('office:name'), str(anno_no))
  #add text
  bk.append(Span(s))
  #comment end 
  ee = etree.Element(CN("office:annotation-end"))
  ek = Span(xmlnode=ee)
  ek.set_attr(CN('office:name'), str(anno_no))
  #add comment to paragraph
  para.append(bk)
  #add  base_txt
  para.append(ek) 

def add_link_toc(doc_body, str, bk_str): #add link to table of content
  es = etree.Element(CN("text:bookmark-start"))
  bk = Span(xmlnode=es)
  bk.set_attr(CN('text:name'), bk_str)
  #header 
  h = Heading(str, outline_level=1 )
  h.append(bk) #append bookmark to heading
  #bookmark end 
  ee = etree.Element(CN("text:bookmark-end"))
  bk = Span(xmlnode=ee)
  bk.set_attr(CN('text:name'), bk_str)
  h.append(bk) #append bookmark to heading
  #add heading to body
  doc_body.append(h)
  
ptn_rfc = r"RFC "
p_rfc = re.compile(ptn_rfc)
def ref_link_rfc(str): #no dictionary
  sloc = 0
  p = Paragraph('')
  if str.find('RFC ') == -1: 
    p.append_text(str)
    return p
  iter = re.finditer(p_rfc, str) #get all matchs
  htmp = ""
  tmp_l = []
  for match in iter:
    htmp = ""
    try:
      #format sample is 'RFC 2327.' or 'RFC 2327 '
      tmp = str[match.start():]
      tmp = tmp.replace('.', ' ')
      tmp = tmp.replace(',', ' ')
      tmp = tmp.replace(';', ' ')
      tmp = tmp.replace('-', ' ')
      tmp = tmp.replace(')', ' ')
      tmp_l = tmp.split(' ')
      n = int(tmp_l[1]) 
       htmp = 'https://tools.ietf.org/html/rfc{0}'.format(n) #html
#      htmp = 'http://www.ietf.org/rfc/rfc{0}.txt'.format(n) #txt
    except:
      print tmp_l
      print 'Get RFC reference no. exception:' + str
    finally:
      pass
    p.append_text(str[sloc:match.start()-1] + ' ') #Why space?
    #4 is number of RFC
    h = Hyperlink(text=str[match.start():match.end()+4], href=htmp)
    p.append(h)
    sloc = match.end() + 4 #next of RFC 
    if sloc >= len(str)-1:
      break
  p.append_text(str[sloc:])
  return p

def add_def_ref(str, def_list, body):
  add = ""
  for elem in def_list:  
    if str.find(elem[0]) > -1:
      add += '[' + elem[0] + ']' + elem[1] 
  p = ref_link_rfc(str)
  if add != "":
    p.append_text(add)
#    add_comment(add, p)
  body.append(p)

#table of contents
def add_table_cnt(body, toc):
  for i in toc:
    prow = Paragraph('  ')
    hlink = Hyperlink(text=i[0])
    hlink.href = '#' + i[0]
    prow.append(hlink)
    if len(i[0]) <= 5:
      prow.append_text("\t\t" + i[1])
    else:
      prow.append_text("\t" + i[1])
    body.append(prow)

def add_heading(s, doc_body, toc):
  for i in toc:
    tmp = i[0] + ' ' + i[1]
    if s.find(tmp) > -1:
      #bookmark start  
      es = etree.Element(CN("text:bookmark-start"))
      bk = Span(xmlnode=es)
      bk.set_attr(CN('text:name'), i[0])
      #header 
      level = len(i[0].split('.'))
      h = Heading(text=i[0] + ' ' + i[1], outline_level=level )
      h.append(bk) #append bookmark to heading
      #bookmark end 
      ee = etree.Element(CN("text:bookmark-end"))
      bk = Span(xmlnode=ee)
      bk.set_attr(CN('text:name'), i[0])
      h.append(bk) #append bookmark to heading
      #add heading to body
      doc_body.append(h)
      return True
  return False

# MAIN

argvs = sys.argv  # list of command line
argc = len(argvs) # prameter number

if argc != 2:
  print_help()
  sys.exit()

if not os.path.exists(argvs[1]):
  print "no source file"
  sys.exit() 

#open files
infile = open(argvs[1], "r")
read_line = infile.readlines()
infile.close()
fname = argvs[1].split('.')
odt = ezodf.opendoc(filename = 'base.odt')

print "delete page feed and header and footer"
line_wo_lf = []
flag = 0
for line in read_line:
  if flag == 1: #next line of page feed
    flag = 0
    continue
  if line.find('\f') > -1: #page feed
    line_wo_lf.pop() #delete last line of page feed
    flag = 1
    continue
  line_wo_lf.append(line)
print 'lines:' + str(len(line_wo_lf))

print "Make list of Table of Content"
def_str = 'Table of Content'
end_of_contents = '1 Introduction'
table_content = []
i = 0
for line in line_wo_lf:
  if line.find(def_str) > -1:
    break
  else:
    i += 1
i += 2 #move to 1st element of contents
start_toc = i

print 'get table of content'
index = i
for i in range(index, len(line_wo_lf)-1):
  s = line_wo_lf[i]
  if s == '':
    continue
  if s.find(end_of_contents) > -1:
    break
  else:
    s = s.lstrip() 
    s = s.replace('  ', '@') 
    s = s.replace('..', '@') 
    cnt = s.split('@')
    ncnt = []
    for s in cnt:
      stmp = s.strip()
      if stmp != '' and stmp != '.':
        ncnt.append(stmp)
    if len(ncnt) >= 2: 
      cnt = ncnt[:2] 
      table_content.append(cnt)
#print table_content

print 'find end table of content'
end_toc = 0
src = line_wo_lf
for i in range(start_toc+1, len(src)-1):
  if src[i].find(table_content[0][0] + ' ' + table_content[0][1]) > -1: 
    end_toc = i
    break 
print start_toc , end_toc

print "find Definitions"
#find area
i = 0
for t in table_content:
  if t[1] == 'Definitions':
    break 
  i += 1
end_def_str = table_content[i+1][0] + ' ' + table_content[i+1][1]
#find definision
pattern = r' {2,}' #case1 some spaces
repattern = re.compile(pattern)
flag = 0
def_txt = ""
def_dic = []
for s in line_wo_lf:
  if s.find('Definitions') > -1: #start of definition
    flag += 1
  if flag < 2: #after 2nd keyword is target(1st is table of content)
    continue
  if s.find(end_def_str) > -1: #end of definition
    break
  if s == "\n":
    if def_txt != '':
      def_txt = re.sub(repattern, ' ', def_txt) #replace spaces to a space
      if def_txt.find('(') > -1: #contains ryakugo
        tmp = def_txt.replace('(', ':')
        tmp = tmp.replace(')', ':')
        tmp = tmp.split(':') #separate key and definition
        if len(tmp) >= 4:
          tmp2 = []
          tmp2.append(tmp[2].strip())
          tmp2.append(tmp[1].strip() + ' ' + tmp[3].strip())
          tmp2[1] = tmp2[1].replace('\n', '')
          tmp2[1] = tmp2[1].replace('  ', ' ')
          if len(tmp2[0]) >= 2:
            def_dic.append(tmp2)
      else:
        tmp = def_txt.split(':') #separate key and definition
        if len(tmp) >= 2 and tmp[0] != '':
          tmp[0] = tmp[0].strip()
          tmp[1] = tmp[1].strip()
          tmp[1] = tmp[1].replace('\n', '')
          if len(tmp[0]) >= 2:
            def_dic.append(tmp)

      def_txt = '' #some definitions accross page are vanished
    continue
  def_txt += s 
print "definitions:" + str(len(def_dic))
#print  def_dic

print 'make paragraph'
last_str = ''
para = ''
i = 0
for s in line_wo_lf:
  i += 1
  if s.find("Table of Contents") > -1:
    add_link_toc(odt.body, s, "#table_of_contents") #link to table of content
    continue
  if i == start_toc + 1: #next to title 'Table of Content'
    add_table_cnt(odt.body, table_content)
    continue
  if i < end_toc and i > start_toc + 1: #in table of content
    continue    
  if add_heading(s, odt.body, table_content):
    last_str = ''
    continue
  if s != "\n":
    para += s
  if s == "\n" and last_str == "\n": #omit duplicate \n
    continue
  elif s == "\n" and last_str !='':
    para += para[:len(s)-1] #delete last '\n'
    add_def_ref(para, def_dic, odt.body)
    para = "\n" #add '\n' at head of paragraph
  last_str = s
print 'Paragraphs:' + str(i)

#save file
odt.saveas(filename = 'cmt_' + fname[0] + '.odt')
sys.exit()
