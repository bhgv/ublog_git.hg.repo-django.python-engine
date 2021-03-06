# -*- coding: utf8 -*-
#/*-------------------------------------------------------------------------
#Coco.py -- the Compiler Driver
#Compiler Generator Coco/R,
#Copyright (c) 1990, 2004 Hanspeter Moessenboeck, University of Linz
#extended by M. Loeberbauer & A. Woess, Univ. of Linz
#ported from Java to Python by Ronald Longo
#
#This program is free software; you can redistribute it and/or modify it
#under the terms of the GNU General Public License as published by the
#Free Software Foundation; either version 2, or (at your option) any
#later version.
#
#This program is distributed in the hope that it will be useful, but
#WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
#or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
#for more details.
#
#You should have received a copy of the GNU General Public License along
#with this program; if not, write to the Free Software Foundation, Inc.,
#59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
#As an exception, it is allowed to write an extension of Coco/R that is
#used as a plugin in non-free software.
#
#If not otherwise stated, any source code generated by Coco/R (other than
#Coco/R itself) does not fall under the GNU General Public License.
#-------------------------------------------------------------------------*/
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import os
import os.path

import re

from agd.config import config

from Scanner import *
from Parser import *



srcName = sys.argv[1]
dirName, fileName = os.path.split(srcName)

# Initialize the Scanner
try:
   s = open( fileName, 'r' )
   try:
      strVal = s.read( )
   except IOError:
      sys.stdout.write( '-- Compiler Error: Failed to read from source file "%s"\n' % fileName )

   try:
      s.close( )
   except IOError:
      raise RuntimeError( '-- Compiler Error: cannot close source file "%s"' % fileName )
except IOError:
   raise RuntimeError( '-- Compiler Error: Cannot open file "%s"' % fileName )


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

Errors.Init(parser, fileName, dirName, False, parser.getParsingPos, parser.errorMessages)

parser.Parse( scanner )

if Errors.count != 0:
   Errors.Summarize( scanner.buffer )
   sys.exit(1)

