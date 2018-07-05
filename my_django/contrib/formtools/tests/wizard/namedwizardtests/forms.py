import os
import tempfile

from my_django import forms
from my_django.core.files.storage import FileSystemStorage
from my_django.forms.formsets import formset_factory
from my_django.http import HttpResponse
from my_django.template import Template, Context

from my_django.contrib.auth.models import User

from my_django.contrib.formtools.wizard.views import NamedUrlWizardView

temp_storage_location = tempfile.mkdtemp(dir=os.environ.get('DJANGO_TEST_TEMP_DIR'))
temp_storage = FileSystemStorage(location=temp_storage_location)

class Page1(forms.Form):
    name = forms.CharField(max_length=100)
    user = forms.ModelChoiceField(queryset=User.objects.all())
    thirsty = forms.NullBooleanField()

class Page2(forms.Form):
    address1 = forms.CharField(max_length=100)
    address2 = forms.CharField(max_length=100)
    file1 = forms.FileField()

class Page3(forms.Form):
    random_crap = forms.CharField(max_length=100)

Page4 = formset_factory(Page3, extra=2)

class ContactWizard(NamedUrlWizardView):
    file_storage = temp_storage

    def done(self, form_list, **kwargs):
        c = Context({
            'form_list': [x.cleaned_data for x in form_list],
            'all_cleaned_data': self.get_all_cleaned_data()
        })

        for form in self.form_list.keys():
            c[form] = self.get_cleaned_data_for_step(form)

        c['this_will_fail'] = self.get_cleaned_data_for_step('this_will_fail')
        return HttpResponse(Template('').render(c))

class SessionContactWizard(ContactWizard):
    storage_name = 'my_django.contrib.formtools.wizard.storage.session.SessionStorage'

class CookieContactWizard(ContactWizard):
    storage_name = 'my_django.contrib.formtools.wizard.storage.cookie.CookieStorage'

