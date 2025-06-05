from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Turno, Especialidad, Doctor
class RegistroForm(UserCreationForm):
    ROLES = (
        ('paciente', 'Paciente'),
        ('doctor', 'Doctor'),
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
    
    class Meta:
        model = Doctor
        fields = ['especialidad']

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['email'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
        )
        doctor = super().save(commit=False)
        doctor.user = user
        if commit:
            doctor.save()
        return doctor