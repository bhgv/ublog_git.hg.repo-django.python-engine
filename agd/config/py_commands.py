
from pygments import util
from pygments import highlight
from pygments.lexers import get_lexer_by_name, get_all_lexers
from pygments.formatters import HtmlFormatter




class Ext:
   used_css = []
   lang_names = []
   err_nolang = ""

   def __init__(self):
      for (lang, lang_aliases, filenames, mimetypes) in get_all_lexers():
         self.lang_names.append(lang)
         for lang in lang_aliases:
            self.lang_names.append(lang)
      
      text = u"<br>-V-----------------------------V-<br>"
      text += u"ERROR: The lang (%s) may be only:<br>"
      for lang in self.lang_names:
         text += u"&nbsp;" + lang + u"<br>"
      self.err_nolang = text + u"-A-----------------------------A-<br>"

   def code_coloriser(self, pars):
      lang = pars[0].strip()
      text = ''
      i = len(pars) - 1
      while i > 0:
         text += pars[i]
         i -= 1
   
      if lang == '' and (lang not in self.lang_names):
         return {'html': lang + " " + text}
      #return text

      try:
         lexer = get_lexer_by_name(lang, stripall=True)
      except util.ClassNotFound:
         return {'html': self.err_nolang % (lang, )}
   
      formatter = HtmlFormatter(linenos=True, cssclass=lang) #, cssclass="source")
      result = highlight(text, lexer, formatter)

      if lang in self.used_css:
         return {'html': result}
      else:
         self.used_css.append(lang)
         return {'css': HtmlFormatter().get_style_defs('.' + lang), 'html': result}

   def reset(self):
      self.used_css = []

   
ext = Ext()


py_commands = {
    r'py_commands_reset': ext.reset,
    r'\code_colorise': ext.code_coloriser,
#    '': ,
};


