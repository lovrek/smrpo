from django.contrib.auth.models import User
from django.forms.models import BaseModelFormSet
from django.forms.widgets import HiddenInput

from applications.models import ResultsMatura, ResultsCourse
from students.models import Student, Address, Applications
from django import forms


class PersonalInformationForm(forms.ModelForm):
    male = forms.TypedChoiceField(
        coerce=lambda x: x and (x.lower() != 'false'),
        choices=((False, 'Ženski'), (True, 'Moški')),
        widget=forms.RadioSelect
    )

    class Meta:
        model = Student
        fields = ["second_last_name", "male", "nationality", "emso", "date_of_birth",
                  "city_of_birth", "country_of_birth",
                  "phone_number", "finished_education"]

    def __init__(self, *args, **kwargs):
        super(PersonalInformationForm, self).__init__(*args, **kwargs)
        self.fields['emso'].required = False
        self.fields['emso'].widget.attrs['required'] = "false"


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name"]


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        exclude = []

    def __init__(self, *args, **kwargs):
        region = kwargs.pop('region', None)
        post = kwargs.pop('post', None)
        super(AddressForm, self).__init__(*args, **kwargs)
        self.fields['region'].initial = region
        self.fields['post'].initial = post
        self.fields['house_number'].widget.attrs['min'] = 1


class StudyProgramForm(forms.ModelForm):
    irregular = forms.TypedChoiceField(
        coerce=lambda x: x and (x.lower() != 'false'),
        choices=((False, 'Redni'), (True, 'Izredni')),
        widget=forms.RadioSelect,
        initial=False
    )

    class Meta:
        model = Applications
        fields = ["study_program", "irregular", "priority"]

    def __init__(self, *args, **kwargs):
        priority = kwargs.pop('priority', None)
        super(StudyProgramForm, self).__init__(*args, **kwargs)
        self.fields['priority'].widget = HiddenInput()
        self.fields['priority'].initial = priority
        self.fields['irregular'].label = "Način študija"


class ResultsMaturaForm(forms.ModelForm):
    is_general = forms.TypedChoiceField(
        coerce=lambda x: x and (x.lower() != 'false'),
        choices=((True, 'Splošna'), (False, 'Poklicna')),
        widget=forms.RadioSelect,
        initial=True
    )
    student_type_field = forms.IntegerField()

    class Meta:
        model = ResultsMatura
        fields = ["general_success_3", "general_success_4", "is_general", "passed", "matura", "student_type_field"]

    def __init__(self, *args, **kwargs):
        is_general = kwargs.pop('is_general', True)
        type = kwargs.pop('type', None)
        super(ResultsMaturaForm, self).__init__(*args, **kwargs)
        self.fields['general_success_3'].widget.attrs['min'] = 1
        self.fields['general_success_3'].widget.attrs['max'] = 5
        self.fields['general_success_4'].widget.attrs['min'] = 1
        self.fields['general_success_4'].widget.attrs['max'] = 5
        self.fields['matura'].widget.attrs['min'] = 0
        self.fields['matura'].widget.attrs['max'] = 34
        self.fields['is_general'].label = "Tip"
        self.fields['is_general'].initial = is_general
        self.fields['student_type_field'].initial = type

    def save(self, commit=True):
        # do something with self.cleaned_data['is_general']
        m = super(ResultsMaturaForm, self).save(commit=False)
        if self.cleaned_data['is_general'] and self.cleaned_data['student_type_field'] and self.cleaned_data['student_type_field'] != "":
            m.student_type_profession = None
            m.student_type = self.cleaned_data['student_type_field']
        elif self.cleaned_data['student_type_field'] and self.cleaned_data['student_type_field'] != "":
            m.student_type=None
            m.student_type_profession = self.cleaned_data['student_type_field']
        if commit:
            m.save()
        return m


class ResultsCourseForm(forms.ModelForm):
    is_general = forms.TypedChoiceField(
        coerce=lambda x: x if type(x) == type(True) else x and (x.lower() != 'false'),
        choices=((True, 'Splošni'), (False, 'Poklicni')),
        widget=forms.RadioSelect,
        initial=True
    )
    type_course_field = forms.IntegerField()

    class Meta:
        model = ResultsCourse
        fields = ["course", "success_course_3", "success_course_4", "is_general", "passed", "result_on_matura", "type_course_field"]

    def __init__(self, *args, **kwargs):
        super(ResultsCourseForm, self).__init__(*args, **kwargs)
        self.fields['success_course_3'].widget.attrs['min'] = 1
        self.fields['success_course_3'].widget.attrs['max'] = 5
        self.fields['success_course_4'].widget.attrs['min'] = 1
        self.fields['success_course_4'].widget.attrs['max'] = 5
        self.fields['is_general'].label = "Tip"

    def save(self, commit=True):
        # do something with self.cleaned_data['is_general']
        m = super(ResultsCourseForm, self).save(commit=False)
        if self.cleaned_data['is_general'] and self.cleaned_data['type_course_field'] and self.cleaned_data['type_course_field'] != "":
            m.type_course_profession = None
            m.type_course = self.cleaned_data['type_course_field']
        elif self.cleaned_data['type_course_field'] and self.cleaned_data['type_course_field'] != "":
            m.type_course = None
            m.type_course_profession = self.cleaned_data['type_course_field']
        if commit:
            m.save()
        return m