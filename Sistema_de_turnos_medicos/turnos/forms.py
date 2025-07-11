from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Turno, Especialidad, Doctor
from django.forms import DateInput, TimeInput

class TurnoForm(forms.ModelForm):
    class Meta:
        model = Turno
        fields = ['fecha', 'hora', 'doctor']

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

class SugerirTurnoForm(forms.ModelForm):
    class Meta:
        model = Turno
        fields = ['fecha', 'hora']
        widgets = {
            'fecha': DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'hora': TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.doctor = kwargs.pop('doctor', None)
        self.paciente = kwargs.pop('paciente', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        turno = super().save(commit=False)
        turno.doctor = self.doctor
        turno.paciente = self.paciente
        turno.estado = 'pendiente' 
        turno.especialidad = self.doctor.especialidad
        if commit:
            turno.save()
        return turno


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


class ReservarTurnoForm(forms.ModelForm):
    class Meta:
        model = Turno
        fields = []  

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        

class CrearFichaForm(forms.ModelForm):
    class Meta:
        model = Turno
        fields = ['fecha', 'hora']
        widgets = {
            'fecha': DateInput(attrs={'type': 'date'}),
            'hora': TimeInput(attrs={'type': 'time'}),
        }

    def __init__(self, *args, **kwargs):
        self.doctor = kwargs.pop('doctor', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        ficha = super().save(commit=False)
        ficha.doctor = self.doctor
        ficha.especialidad = self.doctor.especialidad
        if commit:
            ficha.save()
        return ficha



