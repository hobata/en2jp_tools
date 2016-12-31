# PDF annotation converter
# -*- coding: utf-8 -*-

import sys, re, time

#Location
#/usr/local/lib/python2.7/dist-packages/PyPDF2/pdf.py
from PyPDF2 import PdfFileWriter, PdfFileReader, PdfFileMerger

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import cm, inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def print_help():
  print "This program needs one parameter."
  print "Usage:"
  print " python pdfxx.py [filename]"
  print "Parameter:"
  print " filename: source filename"
  print "ex. IR.94-v10.0.pdf"
  print "output file ex. cmt_IR.94-v10.0.pdf\n"

#Document defineed strings
head_of_definition = 'Definition of Terms'
head_of_document = 'Document Cross'
tail_of_document = 'IMS Feature'
ref_header_word = 'GSM Association'

org_pdf_filename = 'blank.pdf'

def add_lf(s, num):
  start = 0
  print len(s)
  while len(s) > start + num:
    for i in range(num, 1, -1):
      if s[i + start] == ' ':
        s = s[0:i+start-1] + "\n" + s[i+start+1:]
        start += i  + 1
        break
  else:
    return s

#make annitation page
def make_anno_page_table(def_list):
  data_t = [['Term', 'Description']]
  paras = []
  anno_pdf_filename = 'anno.pdf'
  doc = SimpleDocTemplate(anno_pdf_filename, pagesize=letter,
                        rightMargin=72,leftMargin=72,
                        topMargin=72,bottomMargin=18)
  Story=[]
  styles=getSampleStyleSheet()
  styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
  i = 0
  for key in def_list.keys(): #hyperlink for reference
    s = def_list[key]
    loc = s.find(ref_header_word) #delete header from reference text
    if loc > -1: #delete header from reference text
      s = s[:loc-1]
    if key.find('3GPP ') > -1: #with a space
      tmp = key.replace(".", ' ')
      word = tmp.split(' ')
      try:
        n = int(word[2])
        if word[3].find('-') > -1: #ex. 523-1
          tmp = 'http://www.3gpp.org/ftp/Specs/archive/{0}_series/{0}.{1}'.format(n, word[3])
        else: #ex. 300
          m = int(word[3])
          tmp = 'http://www.3gpp.org/ftp/Specs/archive/{0}_series/{0}.{1:03d}'.format(n, m)
        s = '<a href="' + tmp + '" color="blue">[' + key + ']</a>' + ' ' + s
        ptext = '<font size=10>%s</font>' % s
        paras.append(Paragraph(ptext, styles["Normal"]))
        i += 1
      except:
        print '3GPP reference int exception:' + s
      finally:
        pass
    elif key.find('RFC ') > -1:
      word = key.split(' ')
      try:
        n = int(word[1])
        tmp = 'https://tools.ietf.org/html/rfc{0}'.format(n) #html
        s = '<a href="' + tmp + '" color="blue">[' + key + ']</a>' + ' ' + s
#        s = '<a href="' + tmp + '" color="blue">[' + key + ']</a>' + ' ' +  "document description"
        ptext = '<font size=10>%s</font>' % s
        i += 1
        paras.append(Paragraph(ptext, styles["Normal"]))
      except:
        print 'RFC reference int exception:' + s
      finally:
        pass
    else:
      s = add_lf(s, 60)
      data_t.append([key, s])
  if len(data_t) >= 0:
    t = Table(data_t)
    t.hAlign = 'LEFT'
    Story.append(t)
  print len(paras)
  Story.append(Spacer(1, 10))
  for p in paras:
    Story.append(p)
    Story.append(Spacer(1, 3))
  doc.build(Story)
  return anno_pdf_filename

def remove_header(s):
  iptn = r"^GSM.*of [0-9]{1,4}" #page header and footer
  s = re.sub(iptn , '', s)
  return s.strip()


##### MAIN ####
start_time = time.time()

#check parameter
argvs = sys.argv  # list of command line
argc = len(argvs) # prameter number
if argc != 2:
  print_help()
  sys.exit()

#open input file and get width and height
print 'read pdf file'
output = PdfFileWriter()
input1 = PdfFileReader(open(argvs[1], "rb"))
pageObj = input1.getPage(0)
pageWidth, pageHeight = A4 

#make pdf file with a blank page
existing_pdf = PdfFileWriter()
existing_pdf.addBlankPage(width = pageWidth, height = pageHeight)
outputStream = file(org_pdf_filename, "wb")
existing_pdf.write(outputStream)
outputStream.close()

# print how many pages input1 has:
num_page = input1.getNumPages()
print "source pdf file has %d pages." % num_page

pg_txt = []
one_txt = ""
raw_txt = ""
print "Get Document txt" 
for var in range(0, num_page - 1):
  pageObj = input1.getPage(var)
  pdf_txt = pageObj.extractText()
  pdf_txt = pdf_txt.encode('utf-8')
#conversion to get plain strings
  tmp = pdf_txt
  raw_txt += tmp
  tmp = tmp.replace('\n', '')
  tmp = remove_header(tmp)
  pg_txt.append(tmp)
  one_txt += tmp
#print pg_txt
#print one_txt
#print raw_txt

print "Get Definition of Terms " + str(time.time()-start_time)
def_term = {}
start_def = one_txt.rfind(head_of_definition) + len(head_of_definition)
end_def = one_txt.rfind(head_of_document)
#print one_txt[start_def:end_def]
d_ptn = r"[0-9]{0,1}[a-z]{0,1}[A-Z]{2,7}" #find term
r_ptn = re.compile(d_ptn)
tmp = one_txt[start_def:end_def]
print tmp
iter = re.finditer(r_ptn, tmp)
i = 0
key = ""
lastkey = ""
lastend = 0
ref_list = []
for match in iter:
  i += 1
  key = tmp[match.start():match.end()]
  if i > 1:
    if match.start()-1 > lastend +1 + 10: #description isn't short
      if lastkey != "":
        def_term[lastkey] = tmp[lastend+1:match.start()-1]
      lastkey = key
      lastend = match.end()
def_term[key] = tmp[lastend+1:len(tmp)-5]
#print def_term

print "Get Reference " + str(time.time()-start_time)
d_ptn = r"\n+" #find term
r_ptn = re.compile(d_ptn)
tmp = re.sub(r_ptn, "\n", raw_txt)
tmp = tmp.replace(" \n", " ")
#print tmp
head_of_ref = "Document Cross"
tail_of_ref = "IMS Feature"
start_ref = tmp.rfind(head_of_ref)
end_ref = tmp.rfind(tail_of_ref)
ref_list = tmp[start_ref:end_ref].splitlines()
#print ref_list
tmp = []
flag = 0
for i in range(0, len(ref_list)-2):
  if flag == 1:
    flag = 0
    continue
  if ref_list[i].strip() == '-':
    tmp[-1] += ref_list[i] + ref_list[i+1]
    flag = 1
  else:
    tmp.append(ref_list[i].strip())
ref_list = tmp
#print ref_list

print "Make Reference Dic."
j = 0
ref_dic = {}
doc_no = 1
term = ""
desc = ""
for i in range(0, len(ref_list)-1):
  if j > i:
    continue
  if ref_list[i] == str(doc_no): #ex. "1"
    term = ref_list[i+1] 
    for j in range(i+2, len(ref_list)-1): #desc has some strings
      if ref_list[j] == str(doc_no+1): #ex. "2"
        ref_dic[term] = desc
        desc = ""
        doc_no += 1
        break
      else:
        desc += ref_list[j] 
ref_dic[term] = desc
print ref_dic

print "Set Def. and Ref. to each page " + str(time.time()-start_time)
index = 0
for var in range(0, num_page - 1):
  index += 1
  pageObj = input1.getPage(var)
  output.addPage(pageObj)
# print text of each page
# print pg_txt

#find definition and reference document
  out_list = {}
  page_txt = pg_txt[index-1]
  for key in def_term.keys():
    if page_txt.find(key) != -1:
      out_list[key] = def_term[key]
  for key in ref_dic.keys():
    if page_txt.find(key) != -1:
      out_list[key] = ref_dic[key]
# print out_list

#add new page with definition and reference document text
  t_filename = make_anno_page_table(out_list)

#merge to blank page and save
  tmp_pdf_c = PdfFileReader(file(t_filename, "rb"))
  existing_pdf = PdfFileReader(file(org_pdf_filename, "rb"))
  tmp_page = existing_pdf.getPage(0)
  tmp_page.mergePage(tmp_pdf_c.getPage(0))
  output.addPage(tmp_page)

print 'save pdf file ' + str(time.time()-start_time)
outputStream = file('cmt_' + argvs[1], "wb")
output.write(outputStream)
print time.time()-start_time
