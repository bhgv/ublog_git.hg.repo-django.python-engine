# -*- coding:utf-8 -*-
import sys
#reload(sys)
#sys.setdefaultencoding("utf-8")

import os
import os.path

import re

from agd.config import config

from agd.Scanner import *
from agd.Parser import *



#srcName = sys.argv[1]
#dirName, fileName = os.path.split(srcName)

# Initialize the Scanner
#try:
#   s = open( fileName, 'r' )
#   try:
#      strVal = s.read( )
#   except IOError:
#      sys.stdout.write( '-- Compiler Error: Failed to read from source file "%s"\n' % fileName )
#
#   try:
#      s.close( )
#   except IOError:
#      raise RuntimeError( '-- Compiler Error: cannot close source file "%s"' % fileName )
#except IOError:
#   raise RuntimeError( '-- Compiler Error: Cannot open file "%s"' % fileName )


def to_html(strVal):
   #return markdown(value, safe_mode='escape')
   
   f = open(config.config_path + "default.txt", "r")
   if f != None:
      s = f.read()
      f.close()
   
      i = len(s) - 1
      while i >= 0 and (s[i] == '\n' or s[i] == '\r'):
         i -= 1
      i += 1
   
      strVal = s[0:i] + strVal


   re_incl_m = re.compile(config.include_regular_mask)

   re_res = re_incl_m.search(strVal)
   while re_res != None:
      f = open(config.config_path + re_res.group(1) + ".txt", "r")
      if f != None:
         s = f.read()
         f.close()
      
         i = len(s) - 1
         while i >= 0 and (s[i] == '\n' or s[i] == '\r'):
            i -= 1
         i += 1
      
         strVal = strVal[0:re_res.start(0)] + s[0:i] + strVal[re_res.end(0):]
   
      re_res = re_incl_m.search(strVal)
   
   scanner = Scanner( strVal )
   parser  = Parser( )

   #Errors.Init(parser, fileName, dirName, False, parser.getParsingPos, parser.errorMessages)
   Errors.Init(parser, "", "", False, parser.getParsingPos, parser.errorMessages)

   out = parser.Parse( scanner )

   if Errors.count != 0:
      Errors.Summarize( scanner.buffer )
      return out + u"<br>Error"
   #sys.exit(1)
   else:
      #print out
      return out


   
   
   
#try:
#    from agd import markdown
#
#    def to_html(value):
#        return markdown(value, safe_mode='escape')
#except ImportError:
#    from markdown import markdown
#
#    def to_html(value):
#        return markdown(value, safe_mode=True)

def name():
    return 'agd'
