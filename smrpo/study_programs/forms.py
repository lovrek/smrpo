from django import forms
from .models import StudyProgram, Slots, TypeRequirements
from .models import Course
from django.core.validators import MaxValueValidator, MinValueValidator
from django.forms import ModelChoiceField, FloatField, BooleanField, ModelMultipleChoiceField, SelectMultiple
from django.core.exceptions import ValidationError
from information.models import Profession


class SlotsForm(forms.ModelForm):
    class Meta:
        model = Slots
        fields = '__all__'


class StudyProgramForm(forms.ModelForm):
    class Meta:
        model = StudyProgram
        exclude = ["irregular_slots", "regular_slots", "general_matura", "profession_matura", "type_requirements", "priority_course",
                   "deleted"]


class RequirementsTypeForm(forms.Form):
    type = ModelChoiceField(queryset=TypeRequirements.objects.all(), empty_label='Izberite tip pogoja', required=True, label="Tip pogoja")


class Requirement00Form(forms.Form):
    w_matura = FloatField(validators=[MinValueValidator(.0), MaxValueValidator(1.)], label="Utež uspeha mature")
    w_general = FloatField(validators=[MinValueValidator(.0), MaxValueValidator(1.)], label="Utež uspeha v 3. in 4. letniku")

    def clean(self):
        cleaned_data = super(Requirement00Form, self).clean()
        if 'w_matura' in cleaned_data and 'w_general' in cleaned_data:
            val = cleaned_data['w_matura'] + cleaned_data['w_general']
            if not approx_equal(val, 1, 0.001):
                raise ValidationError("Seštevek uteži mora biti enak 1.")
        return cleaned_data


class RequirementP1P3Form(forms.Form):
    profession = ModelChoiceField(queryset=Profession.objects.all(),
                                  empty_label="Izberite poklic",
                                  label="Poklic",
                                  required=False)
    has_priority_course = BooleanField(
        label="Pogoj vsebuje prioritetni predmet", required=False)
    priority_course = ModelChoiceField(queryset=Course.objects.all(),
                                       empty_label="Izberite prioritetni predmet",
                                       label="Prioritetni predmet",
                                       required=False)

    w_gen_matura = FloatField(validators=[MinValueValidator(.0), MaxValueValidator(1.)], label="Utež uspeha splošne mature")
    w_gen_general = FloatField(validators=[MinValueValidator(.0), MaxValueValidator(1.)], label="Utež uspeha v 3. in 4. letniku s splošno maturo")
    w_gen_priority_course_matura = FloatField(
        validators=[MinValueValidator(.0), MaxValueValidator(1.)],
        label="Utež usepeha prioritetnega predmeta na splošni maturi",
        required=False)
    w_gen_priority_course_general = FloatField(validators=[MinValueValidator(.0), MaxValueValidator(1.)], label="Utež uspeha prioritetnega predmeta v 3. in 4. letniku s splošno maturo", required=False)

    w_pro_matura = FloatField(validators=[MinValueValidator(.0), MaxValueValidator(1.)], label="Utež uspeha poklicne mature")
    w_pro_general = FloatField(validators=[MinValueValidator(.0), MaxValueValidator(1.)], label="Utež uspeha v 3. in 4. letniku s poklicno maturo")
    w_pro_priority_course_matura = FloatField(
        validators=[MinValueValidator(.0), MaxValueValidator(1.)],
        label="Utež usepeha prioritetnega predmeta na poklicni maturi",
        required=False)
    w_pro_priority_course_general = FloatField(validators=[MinValueValidator(.0), MaxValueValidator(1.)], label="Utež uspeha prioritetnega predmeta v 3. in 4. letniku s poklicno maturo", required=False)

    matura_courses = ModelMultipleChoiceField(queryset=Course.objects.filter(sifra__startswith="M"),
                                              required=False,
                                              label="Maturitetni predmeti",
                                              widget=forms.CheckboxSelectMultiple)
    w_matura_course = FloatField(validators=[MinValueValidator(.0), MaxValueValidator(1.)], label="Utež maturitetnega predmeta", required=False)

    def clean(self):
        cleaned_data = super(RequirementP1P3Form, self).clean()

        if cleaned_data['w_gen_priority_course_matura'] is not None and cleaned_data['w_gen_priority_course_general'] is not None and\
                        cleaned_data['w_pro_priority_course_matura'] is not None and cleaned_data['w_pro_priority_course_general'] is not None:
            if 'w_gen_matura' in cleaned_data and 'w_gen_general' in cleaned_data:
                val = cleaned_data['w_gen_matura'] + cleaned_data['w_gen_general'] + cleaned_data['w_gen_priority_course_matura'] + cleaned_data['w_gen_priority_course_general']
                if not approx_equal(val, 1, 0.001):
                    raise ValidationError("Seštevek uteži mora biti enak 1.")

            if 'w_pro_matura' in cleaned_data and 'w_pro_general' in cleaned_data:
                val = cleaned_data['w_pro_matura'] + cleaned_data['w_pro_general'] + cleaned_data['w_pro_priority_course_matura'] + cleaned_data['w_pro_priority_course_general']
                if not approx_equal(val, 1, 0.001):
                    raise ValidationError("Seštevek uteži mora biti enak 1.")
        else:
            if 'w_gen_matura' in cleaned_data and 'w_gen_general' in cleaned_data:
                val = cleaned_data['w_gen_matura'] + cleaned_data['w_gen_general']
                if not approx_equal(val, 1, 0.001):
                    raise ValidationError("Seštevek uteži mora biti enak 1.")

            if cleaned_data['w_matura_course'] is None:
                raise ValidationError("Manjka utež maturitetnega predmeta.")
            if 'w_pro_matura' in cleaned_data and 'w_pro_general' in cleaned_data and cleaned_data['w_matura_course'] is not None:
                val = cleaned_data['w_pro_matura'] + cleaned_data['w_pro_general'] + cleaned_data['w_matura_course']
                if not approx_equal(val, 1, 0.001):
                    raise ValidationError("Seštevek uteži mora biti enak 1.")

        return cleaned_data


def approx_equal(a, b, tol):
    return abs(a-b) <= (abs(a)+abs(b))/2 * tol