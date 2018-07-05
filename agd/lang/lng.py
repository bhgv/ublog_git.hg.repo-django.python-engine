
import time


class VM:
   out_text = ''
   out_css = ''

   Name = ''

   #------------ TL ------------------------------------------------------

   #/* object kinds */

   VARS = 0
   PROCS = 1
   SCOPES = 2
   PY_MOD = 3

   #/* types */

   UNDEF = 0
   INT   = 1
   BOOL  = 2
   STRING = 3

   undefObj = None   #/* object node for erroneous symbols */
   curLevel = 0      #/* nesting level of current scope */

   topScope = None   #/* topmost procedure scope */


   def EnterScope (self):
      scope = {
          'name': "", 
          'type': self.UNDEF, 
          'kind': self.SCOPES, 
          'locals': None, 
          'nextAdr': 3, 
          'next': self.topScope,
          'hash': {}
      }
      self.topScope = scope
      self.curLevel += 1


   def LeaveScope (self):
      self.topScope = self.topScope['next']
      self.curLevel -= 1


   def DataSpace (self):
      return self.topScope['nextAdr'] - 3;


   def NewObj (self, name, kind):
      obj = {
          'name': name,
          'type': self.UNDEF,
          'kind': kind,
          'level': self.curLevel,
          'adr':  None,
          'pars': [],
          'scope': self.topScope,
          'val': None
      }
      #p = self.topScope['locals']
      #while p != None:
      #   if p['name'] == name:
      #      self.SemError(117)
      #   p = p['next']
      #obj['next'] = self.topScope['locals']
      #self.topScope['locals'] = obj
      if kind == self.VARS:
         obj['adr'] = self.topScope['nextAdr']
         self.topScope['nextAdr'] += 1
      
      self.topScope['hash'][name] = obj

      return obj


   def GetObj (self, name):
      scope = self.topScope
      while scope != None:
         if scope['hash'].has_key(name):
            return scope['hash'][name]
      #   obj = scope['locals']
      #   while obj != None:
      #      if obj['name'] == name:
      #         return obj
      #      obj = obj['next']
         scope = scope['next']
      return self.undefObj


   def Obj (self, name):
      obj = self.GetObj(name)
      if obj is self.undefObj:
         obj = self.NewObj(name, self.VARS)
      return obj


   def tl_init (self):
      self.topScope = None
      self.curLevel = 0
      self.undefObj = {
          'name': "",
          'type': self.UNDEF,
          'kind': self.VARS,
          'adr': 0,
          'level': 0,
          'pars': [],
          'next': None
      }
      self.progStart = 0
      self.pc = 1
      self.generatingCode = 1
      self.top = 0
      self.base = 0
      self.out_text = u""
      self.out_css = u""





   #-------- TC --------------------------


   progStart = 0     #/* address of first instruction of main program */
   pc = 1            #/* program counter */

   generatingCode = 1

   #/* operators */

   #PLUS  = 0
   #MINUS = 1
   #TIMES = 2
   #SLASH = 3
   #EQU   = 4
   #LSS   = 5
   #GTR   = 6

   #/* opcodes */

   ADD   =  0
   SUB   =  1
   MUL   =  2
   DIVI  =  3
   EQU   =  4
   LSS   =  5
   GTR   =  6
   LOAD  =  7
   LIT   =  8
   STO   =  9
   CALL  = 10
   RET   = 11
   RES   = 12
   JMP   = 13
   FJMP  = 14
   HALTc = 15
   NEG   = 16
   READ  = 17
   WRITE = 18

   HTML_BLOCK = 19

   LSTR = 20

   PY_CALL = 21
   RJMP  = 22
   RCALL  = 23

   TEXT_BEGIN = 24
   TEXT_END   = 25

   NOP = 100


   code = []
   strings = []
   stack = [None for i in xrange(100000)]
   top = 0
   base = 0


   def Emit (self, op):
      if self.generatingCode != 0:
         #print "+ pc = %d, op = %d" % (self.pc, op)
         #if self.pc >= MEMSIZE - 5) { self.SemError(125); generatingCode = 0; }
         #else 
         while (len( self.code ) - 10) < self.pc:
            self.code.append( self.NOP )
         self.code[self.pc] = op
         self.pc += 1


   def Emit2 (self, op, val):
      if self.generatingCode != 0:
         #print "+ pc = %d, op2 = %d" % (self.pc, op)
         self.Emit(op)
         self.code[self.pc] = val
         self.pc += 1
         #self.code[self.pc] = val / 256
         #self.pc += 1
         #self.code[self.pc] = val % 256
         #self.pc += 1


   def Emit3 (self, op, level, val):
      if self.generatingCode != 0:
         #print "+ pc = %d, op3 = %d" % (self.pc, op)
         self.Emit(op)
         self.code[self.pc] = level
         self.pc += 1
         self.code[self.pc] = val
         self.pc += 1
         #self.code[self.pc] = val / 256
         #self.pc += 1
         #self.code[self.pc] = val % 256
         #self.pc += 1


   def Emit4 (self, op, level, val, pars = []):
      if self.generatingCode != 0:
         #print "+ pc = %d, op3 = %d" % (self.pc, op)
         self.Emit(op)
         self.code[self.pc] = level
         self.pc += 1
         self.code[self.pc] = val
         self.pc += 1
         self.code[self.pc] = pars
         self.pc += 1
         #self.code[self.pc] = val / 256
         #self.pc += 1
         #self.code[self.pc] = val % 256
         #self.pc += 1


   def Fixup (self, adr):
      if self.generatingCode != 0:
         self.code[adr] = self.pc
         adr += 1
         #self.code[adr] = self.pc / 256
         #adr += 1
         #self.code[adr] = self.pc % 256
         #adr += 1


   def Next (self):
      self.pc += 1
      return self.code[self.pc - 1]


   def Next2 (self):
      x = self.code[self.pc]
      self.pc += 1
      return x
      #x = self.code[self.pc]
      #self.pc += 1
      #y = self.code[self.pc]
      #self.pc += 1
      #return x * 256 + y


   def Push (self, val):
      self.stack[self.top] = val
      self.top += 1


   def Pop (self):
      self.top -= 1
      return self.stack[self.top]


   def Up (self, level):
      b = self.base
      while level > 0:
         b = self.stack[b]
         level -= 1
      return b
      
   def ToMatchType (self, v1, v2):
      if v2 == None:
         v2 = 0
      
      t = type(v1).__name__
      if t == "float":
         return float(v2)
      elif t == "int":
         return int(v2)
      elif t == "string":
         t = type(v2).__name__
         mask = u"%s"
         if t == "float":
            mask = u"%f"
         elif t == "int":
            mask = u"%d"
         return mask % (v2,)
      else:
         return v2



   def Interpret (self, pars, commands):
      self.pars = pars
      self.commands = commands

      ptxt_stack = [None for i in xrange(1000)]
      out_text_stack = [None for i in xrange(1000)]
      ptxt_i = 0
      
      ptxt = u''
      cur_par_e = u''
      cur_par_b = u''
      
      first_par = True
      
      call_rets = 0
      
      verbN = 'text'
      
      watchdog = time.clock() + 2
      
   #  int val, a, lev;
      isRun = True

      #self.EnterScope()

      #print ".<br>"
      #print ".<br>"
      #print ".start"
      #print self.topScope
      #print ".<br>"

      #print "Interpreting\n"
      self.pc = self.progStart
      self.base = 0
      self.top = 3
      while isRun:
         if watchdog < time.clock():
            return
         
         #print ".: pc = %d, " % (self.pc, )
      
         nxt = self.Next()
         
         #print "op = %d<br>" % (nxt, )
         
         if nxt == self.LOAD:
            lev = self.Next()
            a = self.Next2()
            t = None
            v = None
            #print "LOAD -> (lev = %d, adr = %s, val = " % (lev, a)
            
            scope = self.topScope
            while scope != None and t == None:
               if scope['hash'].has_key(a):
                  t = scope['hash'][a]
               scope = scope['next']
            if t != None:
               v = t['val']
            if v == None:
               v = 0
            self.Push(v)

            #while t == None and lev >= 0:
            #   t = self.Up(lev)
            #   lev -= 1
            #if t != None:
            #   val = self.stack[self.Up(lev) + a]
            #if val == None:
            #   val = 0
            #self.Push(val)
            #print "%s)<br>" % (val,)
            #self.Push(self.stack[self.Up(lev) + a])
         
         elif nxt == self.LSTR:
            self.Push(self.strings[self.Next2()])
         
         elif nxt == self.LIT:
            v = self.Next2()
            #print "LIT -> %d<br>" % (v,)
            self.Push(v)
         
         elif nxt == self.STO:
            lev = self.Next()
            a = self.Next2()
            v = self.Pop()
            t = None

            scope = self.topScope
            while scope != None and t == None:
               if scope['hash'].has_key(a):
                  t = scope['hash'][a]
               scope = scope['next']
            if t != None:
               t['val'] = v

            #while t == None and lev >= 0:
            #   t = self.Up(lev)
            #   lev -= 1
            #if t != None:
            #   v = self.Pop()
            #   self.stack[t + a] = v
            #print "STO -> (lev = %d, adr = %s, val = %s)<br>" % (lev, a, v)
            #self.stack[self.Up(lev) + a] = self.Pop()
         
         elif nxt == self.ADD:
            v2 = self.Pop()
            v1 = self.Pop()
            self.Push(v1 + self.ToMatchType(v1, v2))
         
         elif nxt == self.SUB:
            v2 = self.Pop()
            v1 = self.Pop()
            self.Push(v1 - self.ToMatchType(v1, v2))
         
         elif nxt == self.MUL:
            v2 = self.Pop()
            v1 = self.Pop()
            self.Push(v1 * self.ToMatchType(v1, v2))
         
         elif nxt == self.DIVI:
            v2 = self.Pop()
            v1 = self.Pop()
            if v2 == 0:
               print "Divide by zero\n"
               isRun = False
            self.Push(v1 / self.ToMatchType(v1, v2))
         
         elif nxt == self.EQU:
            v2 = self.Pop()
            v1 = self.Pop()
            self.Push(v1 == self.ToMatchType(v1, v2))
         
         elif nxt == self.LSS:
            v2 = self.Pop()
            v1 = self.Pop()
            self.Push(v1 < self.ToMatchType(v1, v2))
         
         elif nxt == self.GTR:
            v2 = self.Pop()
            v1 = self.Pop()
            self.Push(v1 > self.ToMatchType(v1, v2))
         
         elif nxt == self.CALL:
            call_rets += 1
            if call_rets > 100:
               return

            lev = self.Next()
            #print "!! lev = %s<br>" % (lev, )
            #lev = self.Up(lev)
            foo = self.Next2()
            pars = self.Next2()
        
            #print "CALL %s<br>%s<br>" % (foo, pars)

            t = None
            scope = self.topScope
            while scope != None and t == None:
            #   print "---VVV---<br> Scope<br>"
            #   print scope
               
               if scope['hash'].has_key(foo):
                  t = scope['hash'][foo]
               scope = scope['next']
            
            if t != None:
               pc = t['adr']
            else:
            #if pc == None:
               print "Internal Error: pc is None!"
               self.out_text += u"\n" + cur_par_e + u'<br>\n' + "Internal Error: pc is None!<br>"
               isRun = False

            #pc = foo['adr']

            scope = t['scope']
            #scope['next'] = self.topScope
            #self.topScope = scope
            #self.curLevel += 1
            self.EnterScope()
            shash = scope['hash']
            scope = self.topScope
            for k in shash.keys():
               scope['hash'][k] = shash[k]

            #print "CALL pc = %d, pnm = " % (pc, )
            #print pars
            #print "<br>-- pc = %d (%d)<br>" % (pc, self.pc)
            #print "<br>"
            pars = t['pars']
            i = len(pars) - 1
            while i >= 0:
               #(pnm, foo, adr) = pars[i]
               (pnm, adr) = pars[i]
               #o = self.NewObj(pnm, self.PROCS)
               #o = self.Obj(pnm)
               o = self.NewObj(pnm, self.PROCS)
               o['adr'] = self.Pop()
               #print scope['hash'][pnm]
               #print "<br>---<br>"
               #o = self.NewObj(pnm[1:], self.VARS)  
               #self.stack[o['level'] + o['adr']] = adr
               #self.stack[foo] = adr
               i -= 1

            self.Push(lev)
            self.Push(self.base)
            self.Push(self.pc)

            self.pc = pc
            self.base = self.top - 3

         
         elif nxt == self.RET:
            call_rets -= 1

            self.LeaveScope()
            #self.topScope = self.topScope['next']
            #self.curLevel -= 1
            
            self.top = self.base
            self.base = self.stack[self.top + 1]
            self.pc = self.stack[self.top + 2]

            #print "RET pc = %d<br>" % (self.pc, )

         
         elif nxt == self.PY_CALL:
            foo = self.Next()
            par_cnt = self.Next()
            pars = []
            while par_cnt > 0:
               #pars.append(self.Next())
               pars.append(self.Pop())
               par_cnt -= 1
            v = foo(pars)

            #css = ""
            #html = ""
            for k in v.keys():
               if k == 'css':
                  #css += "  <style type=\"text/css\">\n%s\n</style>" % (v[k],)
                  self.out_css += v[k]
               elif k == 'html':
                  #html += "%s" % (v[k],)
                  self.out_text += "%s" % (v[k],)
            #self.out_text += "%s %s" % (css, html)

         
         elif nxt == self.RES:
            self.top += self.Next2()

         
         elif nxt == self.JMP:
            self.pc = self.Next2()

         
         elif nxt == self.FJMP:
            a = self.Next2()
            if self.Pop() == 0:
               self.pc = a

         
         elif nxt == self.RJMP:
            v = self.Pop()
            #print "RJMP -> %d<br>" % (v,)
            self.pc = v

         
         elif nxt == self.RCALL:
            pc = self.Pop()

            self.EnterScope()
            
            self.Push(0)
            self.Push(self.base)
            self.Push(self.pc)

            self.pc = pc
            self.base = self.top - 3

            #print "RJMP -> %d<br>" % (v,)
            #self.pc = v

         
         elif nxt == self.HALTc:
            self.out_text += u'\n' + cur_par_e + u'\n'
            isRun = False

         
         elif nxt == self.NEG:
            self.Push(-self.Pop())

         
        # elif nxt == self.READ:
        #    lev = self.Next()
        #    a = self.Next2()
        #    #print "? "
        #    #scanf("%d", &val)
        #    self.stack[self.Up(lev) + a] = val

         
         elif nxt == self.WRITE:
            v = self.Pop()
            t = type(v).__name__
            mask = u"%s"
            if t == "float":
               mask = u"%f"
            elif t == "int":
               mask = u"%d"
            self.out_text += mask % (v,)

         
         elif nxt == self.HTML_BLOCK:
            i = self.Next2()
            p = self.pars[i]
            #if True or ptxt != '':
            if p['cont_par'] or not p['par']:
               if len(ptxt) == 0 and cur_par_b != '':
                  self.out_text += cur_par_b
               #   cur_par_b = cur_par_b
               
               elif len(ptxt) == 0 and verbN == 'text':
                  self.out_text += self.commands["\\par"]['b'] #cur_par_b
                  cur_par_e      = self.commands["\\par"]['e'] #cur_par_b
               ptxt += p[verbN] #.strip()
               self.out_text += p[verbN] #.strip()
            else:
            #   if first_par and p['regular_par']:
            #      p['b'] = self.commands["\\first_par"]['b']
            #      p['e'] = self.commands["\\first_par"]['e']
               #self.out_text += u'\n' + cur_par_e + u'\n' + cur_par_b + ptxt
               if len(ptxt) > 0:
                  self.out_text += u"\n" + cur_par_e + u'\n' #+ cur_par_b + ptxt
               ptxt = p[verbN].strip()
               cur_par_b = p['b']
               cur_par_e = p['e']

               if len(ptxt) > 0:
                  self.out_text += u"\n" + cur_par_b + p[verbN]
            #      if first_par and p['regular_par']:
            #         first_par = False
               
               
               #self.out_text += p['b'] + ptxt + u'\n' + p['e'] + u'\n'
               
   #         print "%s" % (self.Next2())

         
         elif nxt == self.TEXT_BEGIN:
            verbN = 'verb1'
            out_text_stack[ptxt_i] = self.out_text
            ptxt_stack[ptxt_i] = ptxt
            self.out_text = u""
            ptxt = u""
            ptxt_i += 1
            #print "::NOP::"

         
         elif nxt == self.TEXT_END:
            self.Push( self.out_text ) # + ptxt )
            ptxt_i -= 1
            ptxt = ptxt_stack[ ptxt_i ]
            self.out_text = out_text_stack[ ptxt_i ]
            verbN = 'text'
            #print "::NOP::"

         
         elif nxt == self.NOP:
            ptxt = ptxt
            #print "::NOP::"

         
         else:
            self.out_text += u'\n' + cur_par_e + u'\n'
            isRun = False



   #/*--------------------------------------------------------------------------*/
   def get_out(self):
      #print self.out_css
      return {'text': self.out_text, 'css': self.out_css}

#   def __init__(self, pars):
#      self

