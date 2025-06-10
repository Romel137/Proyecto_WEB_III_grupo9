from django import forms
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Turno, Especialidad, Doctor
<<<<<<< HEAD
from django import forms
from .models import Especialidad
from .models import Doctor, Especialidad
=======
from django.forms import DateInput, TimeInput
from django.contrib import messages
from django.core.exceptions import ValidationError
>>>>>>> 77790a5ccc40e6315b54d8a3f6937f65a1630a3f

class RegistroForm(UserCreationForm):
    ROLES = (
        ('paciente', 'Paciente'),
    )
    rol = forms.ChoiceField(choices=ROLES, widget=forms.RadioSelect)

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'rol']

class TurnoForm(forms.ModelForm):
    especialidad = forms.ModelChoiceField(queryset=Especialidad.objects.all(), required=True)

    class Meta:
        model = Turno
        fields = ['especialidad', 'doctor', 'fecha', 'hora']
        widgets = {
            'fecha': DateInput(attrs={'type': 'date'}),
            'hora': TimeInput(attrs={'type': 'time'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'especialidad' in self.data:
            try:
                especialidad_id = int(self.data.get('especialidad'))
                self.fields['doctor'].queryset = Doctor.objects.filter(especialidad_id=especialidad_id)
            except (ValueError, TypeError):
                self.fields['doctor'].queryset = Doctor.objects.none()
        else:
            self.fields['doctor'].queryset = Doctor.objects.none()

class DoctorRegisterForm(forms.ModelForm):
    username = forms.CharField(label='Nombre de usuario')
    password = forms.CharField(widget=forms.PasswordInput)
    email = forms.EmailField(label='Correo electronico')
    first_name = forms.CharField(label='Nombre')
    last_name = forms.CharField(label='Apellido')

    class Meta:
        model = Doctor
        fields = ['especialidad']

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password'],
            email=self.cleaned_data['email'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
        )
        doctor = super().save(commit=False)
        doctor.user = user
        if commit:
            doctor.save()
        return doctor

class DoctorRegistroForm(forms.ModelForm):
    first_name = forms.CharField(label="Nombre")
    last_name = forms.CharField(label="Apellido")
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    especialidad = forms.ModelChoiceField(
        queryset=Especialidad.objects.all(),
<<<<<<< HEAD
        empty_label="Seleccione una especialidad",
        label="Especialidad"
    )

=======
        required=False,
        empty_label="Seleccione una especialidad"
    )
    nueva_especialidad = forms.CharField(
        required=False,
        label="O escriba una nueva especialidad"
    )
>>>>>>> 77790a5ccc40e6315b54d8a3f6937f65a1630a3f
    class Meta:
        model = Doctor
        fields = ['especialidad']
    
    def clean(self):
        cleaned_data = super().clean()
        especialidad = cleaned_data.get('especialidad')
        nueva = cleaned_data.get('nueva_especialidad')

        if not especialidad and not nueva:
            raise forms.ValidationError("Debe seleccionar o ingresar una especialidad.")
        return cleaned_data
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(username=email).exists():
            raise ValidationError("Ya existe un usuario con este correo electrónico.")
        return email
    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['email'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
        )
        especialidad = self.cleaned_data.get('especialidad')
        nueva = self.cleaned_data.get('nueva_especialidad')
        if nueva:

            especialidad, created = Especialidad.objects.get_or_create(nombre=nueva)
        doctor = super().save(commit=False)
        doctor.user = user
<<<<<<< HEAD
        doctor.especialidad = self.cleaned_data['especialidad']
        if commit:
            doctor.save()
        return doctor
    
class EspecialidadForm(forms.ModelForm):
    class Meta:
        model = Especialidad
        fields = ['nombre']
        labels = {
            'nombre': 'Nombre de la Especialidad'
        }
=======
        doctor.especialidad = especialidad

        if commit:
            doctor.save()
        return doctor

class EspecialidadForm(forms.ModelForm):
    class Meta:
        model = Especialidad
        fields = ['nombre']
>>>>>>> 77790a5ccc40e6315b54d8a3f6937f65a1630a3f
