# coding=utf-8
from my_django import forms

class HgDiffForm(forms.Form):
    """
    This form allows to select two revisions in the file log to display a diff
    """
    from_rev = forms.IntegerField(label='', required=False)
    to_rev = forms.IntegerField(label='', required=False)
    
    def __init__(self, filelog, *args, **kwargs):
        super(HgDiffForm, self).__init__(*args, **kwargs)
        lst = []
        for i in range(len(filelog)):
            lst.append((filelog[i]['rev'], filelog[i]['rev']))
        self.REVS = tuple(lst)
        self.fields['from_rev'].widget = forms.RadioSelect(choices=self.REVS)
        self.fields['to_rev'].widget = forms.RadioSelect(choices=self.REVS)
    
    def clean(self):
        cleaned_data = self.cleaned_data
        
        if cleaned_data.get('from_rev') > cleaned_data.get('to_rev'):
            raise forms.ValidationError('The "from" revision must be lower than the "to" revision.')
            del cleaned_data['to_rev']
            del cleaned_data['from_rev']
        return cleaned_data

class HgRepositoryForm(forms.Form):
    """
    This form allows to search in the repositories
    """
    DISPLAY_CHOICES = (
        ('only_member', 'Only repositories I contribute'),
        ('only_owner', 'Only repositories I own')
    )
    search = forms.CharField(max_length=200, required=False)
    
    def __init__(self, user, *args, **kwargs):
        super(HgRepositoryForm, self).__init__(*args, **kwargs)
        if user.is_authenticated() and self.data['display'] != 'all':
            self.fields['display'] = forms.CharField(max_length=11,
                                                    required=False,
                                                    widget=forms.Select(choices=self.DISPLAY_CHOICES))
        for field in self.fields:
            if field == 'search':
                self.fields[field].widget.attrs['style'] = "float: left; width: 30em;"
            else:
                self.fields[field].widget.attrs['style'] = "float: left;"

    def clean_display(self):
        data = self.data['display']
        return data

    def clean_search(self):
        data = self.data['search']
        return data

    def is_valid(self):
        return True
        
    def as_a(self):
        "Returns this form rendered as HTML <tr>s -- excluding the <table></table>."
        return self._html_output(u'%(field)s%(help_text)s%(errors)s', u'%s', '&nbsp;', u'<br />%s', True)
        #return self._html_output(u'%(label)s%(field)s%(help_text)s%(errors)s', u'%s', '&nbsp;', u'<br />%s', True)

        
