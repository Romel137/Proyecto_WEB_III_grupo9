from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Turno, Especialidad, Doctor
from django.forms import DateInput, TimeInput

class RegistroForm(UserCreationForm):
    ROLES = (
        ('paciente', 'Paciente'),
    )
    rol = forms.ChoiceField(choices=ROLES, widget=forms.RadioSelect)
    email = forms.EmailField(label="Correo electrónico", required=True)
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'rol']

from django import forms
from .models import Turno, Especialidad, Doctor
from django.forms.widgets import DateInput, TimeInput

class TurnoForm(forms.ModelForm):
    especialidad = forms.ModelChoiceField(
        queryset=Especialidad.objects.all(),
        required=True,
        label="Especialidad"
    )
    doctor = forms.ModelChoiceField(
        queryset=Doctor.objects.none(),
        required=True,
        label="Doctor"
    )
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
                esp_id = int(self.data.get('especialidad'))
                self.fields['doctor'].queryset = Doctor.objects.filter(especialidad_id=esp_id)
            except (ValueError, TypeError):
                self.fields['doctor'].queryset = Doctor.objects.none()
        elif getattr(self.instance, 'especialidad_id', None):
            self.fields['doctor'].queryset = Doctor.objects.filter(especialidad=self.instance.especialidad)
        else:
            self.fields['doctor'].queryset = Doctor.objects.none()

class DoctorRegistroForm(forms.ModelForm):
    first_name = forms.CharField(label="Nombre")
    last_name = forms.CharField(label="Apellido")
    email = forms.EmailField(label="Correo electrónico")
    password = forms.CharField(widget=forms.PasswordInput)
    especialidad = forms.ModelChoiceField(
        queryset=Especialidad.objects.all(),
        empty_label="Seleccione una especialidad",
        label="Especialidad"
    )
    nueva_especialidad = forms.CharField(required=False, label="Nueva Especialidad")
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
        doctor.especialidad = especialidad
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
