
import sys

class Token( object ):
   def __init__( self ):
      self.kind   = 0     # token kind
      self.pos    = 0     # token position in the source text (starting at 0)
      self.col    = 0     # token column (starting at 0)
      self.line   = 0     # token line (starting at 1)
      self.val    = u''   # token value
      self.next   = None  # AW 2003-03-07 Tokens are kept in linked list


class Position( object ):    # position of source code stretch (e.g. semantic action, resolver expressions)
   def __init__( self, buf, beg, len, col ):
      assert isinstance( buf, Buffer )
      assert isinstance( beg, int )
      assert isinstance( len, int )
      assert isinstance( col, int )
      
      self.buf = buf
      self.beg = beg   # start relative to the beginning of the file
      self.len = len   # length of stretch
      self.col = col   # column number of start position

   def getSubstring( self ):
      return self.buf.readPosition( self )

class Buffer( object ):
   EOF      = u'\u0100'     # 256

   def __init__( self, s ):
      self.buf    = s
      self.bufLen = len(s)
      self.pos    = 0
      self.lines  = s.splitlines( True )

   def Read( self ):
      if self.pos < self.bufLen:
         result = unichr(ord(self.buf[self.pos]) ) #& 0xff)   # mask out sign bits
         self.pos += 1
         return result
      else:
         return Buffer.EOF

   def ReadChars( self, numBytes=1 ):
      result = self.buf[ self.pos : self.pos + numBytes ]
      self.pos += numBytes
      return result

   def Peek( self ):
      if self.pos < self.bufLen:
         return unichr(ord(self.buf[self.pos]) & 0xff)    # mask out sign bits
      else:
         return Scanner.buffer.EOF

   def getString( self, beg, end ):
      s = ''
      oldPos = self.getPos( )
      self.setPos( beg )
      while beg < end:
         s += self.Read( )
         beg += 1
      self.setPos( oldPos )
      return s

   def isertString( self, str, b = -1, e = -1):
      if b == -1:
         b = self.getPos( )
      if e == -1:
         e = b
      i = len(str) - 1
      while i >= 0 and (str[i] == '\n' or str[i] == '\r'):
         i -= 1
      i += 1
      #print "-----------------------------------------------"
      #print "%d - %d, %d" % (b, e, self.getPos( ))
      
      s = self.buf[0:b] + "\n" + str[0:i] + "\n" + self.buf[e:];
      #print "-----"
      #print s
      
      self.setPos(b)
      self.bufLen = len(s)
      self.lines  = s.splitlines( True )
      self.buf = s

   def getPos( self ):
      return self.pos

   def setPos( self, value ):
      if value < 0:
         self.pos = 0
      elif value >= self.bufLen:
         self.pos = self.bufLen
      else:
         self.pos = value

   def readPosition( self, pos ):
      assert isinstance( pos, Position )
      self.setPos( pos.beg )
      return self.ReadChars( pos.len )

   def __iter__( self ):
      return iter(self.lines)

class Scanner(object):
   EOL     = u'\n'
   eofSym  = 0

   charSetSize = 256
   maxT = 39
   noSym = 39
   start = [
     1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  4,  1,  1,  3,  1,  1,
     1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,
     1,  1, 12,  1,  1,  1,  1, 11,  1,  1, 20, 18, 15, 17, 14, 19,
     5,  5,  5,  5,  5,  5,  5,  5,  5,  5,  1, 16,  9, 25, 10,  1,
     1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,
     1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1, 24,  1,  1,  1,
     1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,
     1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  7,  1,  8,  1,  1,
     1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,
     1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,
     1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,
     1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,
     1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,
     1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,
     1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,
     1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,
     -1]


   def __init__( self, s ):
      #self.buffer = Buffer( unicode(s.encode("utf-8"), "utf-8") ) # the buffer instance
      self.buffer = Buffer( s ) # the buffer instance
      #self.buffer = Buffer( unicode(s, "cp1251") ) # the buffer instance
      #self.buffer = Buffer( unicode(s) ) # the buffer instance
      
      self.ch        = u'\0'       # current input character
      self.pos       = -1          # column number of current character
      self.line      = 1           # line number of current character
      self.lineStart = 0           # start position of current line
      self.oldEols   = 0           # EOLs that appeared in a comment;
      self.NextCh( )
      self.ignore    = set( )      # set of characters to be ignored by the scanner
      self.ignore.add( ord(' ') )  # blanks are always white space
      self.ignore.add(32) 
      self.ignore.add(9) 

      # fill token list
      self.tokens = Token( )       # the complete input token stream
      node   = self.tokens

      node.next = self.NextToken( )
      node = node.next
      while node.kind != Scanner.eofSym:
         node.next = self.NextToken( )
         node = node.next

      node.next = node
      node.val  = u'EOF'
      self.t  = self.tokens     # current token
      self.pt = self.tokens     # current peek token

   def NextCh( self ):
      if self.oldEols > 0:
         self.ch = Scanner.EOL
         self.oldEols -= 1
      else:
         self.ch = self.buffer.Read( )
         self.pos += 1
         # replace isolated '\r' by '\n' in order to make
         # eol handling uniform across Windows, Unix and Mac
         if (self.ch == u'\r') and (self.buffer.Peek() != u'\n'):
            self.ch = Scanner.EOL
         if self.ch == Scanner.EOL:
            self.line += 1
            self.lineStart = self.pos + 1
      




   def CheckLiteral( self ):
      lit = self.t.val
      if lit == "\\table":
         self.t.kind = 20
      elif lit == "\\header":
         self.t.kind = 21
      elif lit == "\\align":
         self.t.kind = 22
      elif lit == "\\row":
         self.t.kind = 23
      elif lit == "\\endtable":
         self.t.kind = 24
      elif lit == "\\var":
         self.t.kind = 28
      elif lit == "\\let":
         self.t.kind = 29
      elif lit == "\\def":
         self.t.kind = 30
      elif lit == "\\enddef":
         self.t.kind = 31
      elif lit == "\\if":
         self.t.kind = 32
      elif lit == "\\else":
         self.t.kind = 33
      elif lit == "\\endif":
         self.t.kind = 34
      elif lit == "\\for":
         self.t.kind = 35
      elif lit == "\\endfor":
         self.t.kind = 36
      elif lit == "true":
         self.t.kind = 37
      elif lit == "false":
         self.t.kind = 38


   def NextToken( self ):
      while ord(self.ch) in self.ignore:
         self.NextCh( )
      
      self.t = Token( )
      self.t.pos = self.pos
      self.t.col = self.pos - self.lineStart + 1
      self.t.line = self.line
      if ord(self.ch) < len(self.start):
         state = self.start[ord(self.ch)]
      else:
         state = 1
      buf = u''
      buf += unicode(self.ch)
      self.NextCh()

      done = False
      while not done:
         if state == -1:
            self.t.kind = Scanner.eofSym     # NextCh already done
            done = True
         elif state == 0:
            self.t.kind = Scanner.noSym      # NextCh already done
            done = True
         elif state == 1:
            if (ord(self.ch) <= 9
                 or ord(self.ch) >= 11 and ord(self.ch) <= 12
                 or ord(self.ch) >= 14 and self.ch <= '!'
                 or self.ch >= '#' and self.ch <= '&'
                 or self.ch >= '(' and self.ch <= ')'
                 or self.ch == ':'
                 or self.ch >= '?' and self.ch <= '['
                 or self.ch >= ']' and self.ch <= 'z'
                 or self.ch == '|'
                 or self.ch >= '~' and ord(self.ch) <= 255):
               buf += unicode(self.ch)
               self.NextCh()
               state = 1
            else:
               self.t.kind = 1
               self.t.val = buf
               self.CheckLiteral()
               return self.t
         elif state == 2:
            if (self.ch >= '!' and self.ch <= '+'
                 or self.ch >= '-' and self.ch <= ':'
                 or self.ch >= '<' and self.ch <= '['
                 or self.ch >= ']' and self.ch <= 'z'
                 or self.ch == '|'
                 or self.ch >= '~' and ord(self.ch) <= 254):
               buf += unicode(self.ch)
               self.NextCh()
               state = 2
            else:
               self.t.kind = 2
               self.t.val = buf
               self.CheckLiteral()
               return self.t
         elif state == 3:
            if ord(self.ch) == 10:
               buf += unicode(self.ch)
               self.NextCh()
               state = 4
            else:
               self.t.kind = Scanner.noSym
               done = True
         elif state == 4:
            self.t.kind = 3
            done = True
         elif state == 5:
            if (self.ch >= '0' and self.ch <= '9'):
               buf += unicode(self.ch)
               self.NextCh()
               state = 5
            elif self.ch == '.':
               buf += unicode(self.ch)
               self.NextCh()
               state = 6
            else:
               self.t.kind = 4
               done = True
         elif state == 6:
            if (self.ch >= '0' and self.ch <= '9'):
               buf += unicode(self.ch)
               self.NextCh()
               state = 6
            else:
               self.t.kind = 4
               done = True
         elif state == 7:
            self.t.kind = 5
            done = True
         elif state == 8:
            self.t.kind = 6
            done = True
         elif state == 9:
            self.t.kind = 7
            done = True
         elif state == 10:
            self.t.kind = 8
            done = True
         elif state == 11:
            self.t.kind = 9
            done = True
         elif state == 12:
            self.t.kind = 10
            done = True
         elif state == 13:
            self.t.kind = 11
            done = True
         elif state == 14:
            self.t.kind = 12
            done = True
         elif state == 15:
            self.t.kind = 13
            done = True
         elif state == 16:
            self.t.kind = 14
            done = True
         elif state == 17:
            self.t.kind = 16
            done = True
         elif state == 18:
            self.t.kind = 17
            done = True
         elif state == 19:
            self.t.kind = 18
            done = True
         elif state == 20:
            self.t.kind = 19
            done = True
         elif state == 21:
            self.t.kind = 25
            done = True
         elif state == 22:
            self.t.kind = 26
            done = True
         elif state == 23:
            self.t.kind = 27
            done = True
         elif state == 24:
            if (self.ch >= '!' and self.ch <= '+'
                 or self.ch >= '-' and self.ch <= ':'
                 or self.ch >= '<' and self.ch <= '['
                 or self.ch >= ']' and self.ch <= 'z'
                 or self.ch == '|'
                 or self.ch >= '~' and ord(self.ch) <= 254):
               buf += unicode(self.ch)
               self.NextCh()
               state = 2
            elif ord(self.ch) == 92:
               buf += unicode(self.ch)
               self.NextCh()
               state = 21
            elif self.ch == '{':
               buf += unicode(self.ch)
               self.NextCh()
               state = 22
            elif self.ch == '}':
               buf += unicode(self.ch)
               self.NextCh()
               state = 23
            else:
               self.t.kind = Scanner.noSym
               done = True
         elif state == 25:
            if self.ch == '=':
               buf += unicode(self.ch)
               self.NextCh()
               state = 13
            else:
               self.t.kind = 15
               done = True

      self.t.val = buf
      return self.t

   def Scan( self ):
      self.t = self.t.next
      self.pt = self.t.next
      return self.t

   def Peek( self ):
      self.pt = self.pt.next
      while self.pt.kind > self.maxT:
         self.pt = self.pt.next

      return self.pt

   def ResetPeek( self ):
      self.pt = self.t

