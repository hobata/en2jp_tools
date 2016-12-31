import sys
import os.path

argvs = sys.argv  # list of command line
argc = len(argvs) # prameter number

def param(argvs):
  n = int(argvs[1])
  m = int(argvs[2])
  return n, m

def print_help():
  print "\nThis program needs two parameters.\n"
  print "Usage:"
  print " python doc_conv.py [spec_no_1] [spec.no_2]"
  print "Parameter:"
  print " spec_no_1:specification no.1:ex.36"
  print " spec_no_2:specification no.1:ex.300\n"
  print 'OFFLINE MODE STARTED...'

mode = 0
n = 36
m = 300
if argc == 3:
  mode = 1 #online mode
  n = int(argvs[1])
  m = int(argvs[2])
else:
  mode = 2 #offline mode
  print_help()

#check exist folder
tmp = '{0}_{1:03d}'.format(n, m)
tmp = './' + tmp
if os.path.isdir(tmp):
  print "folder exits\n"
else:
  print "folder not exits\n"
  os.mkdir(tmp)

sys.exit() 

