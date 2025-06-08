from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Turno, Especialidad, Doctor, Perfil
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
    doctor = forms.ModelChoiceField(
        queryset=Doctor.objects.all(),
        label="Doctor",
        widget=forms.Select()
    )

    class Meta:
        model = Turno
        fields = ['doctor', 'fecha', 'hora']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalizar cómo se muestran los doctores en el desplegable
        self.fields['doctor'].label_from_instance = lambda obj: f"Dr. {obj.user.first_name} {obj.user.last_name} - {obj.especialidad.nombre}"

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
    username = forms.CharField(label='Nombre de usuario')
    email = forms.EmailField(label='Correo electrónico')
    password = forms.CharField(widget=forms.PasswordInput)
    first_name = forms.CharField(label='Nombre')
    last_name = forms.CharField(label='Apellido')

    class Meta:
        model = Doctor
        fields = ['especialidad']

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
        )

        perfil = Perfil.objects.create(user=user, es_doctor=True)

        doctor = super().save(commit=False)
        doctor.user = user
        if commit:
            doctor.save()
        return doctor