from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Especialidad(models.Model):
    nombre = models.CharField(max_length=100)
    def __str__(self):
        return self.nombre

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    especialidad = models.ForeignKey(Especialidad, on_delete=models.CASCADE)
    def __str__(self):
        return f"Dr. {self.user.get_full_name()} - {self.especialidad.nombre}"
    
class Paciente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telefono = models.CharField(max_length=20)
    email = models.EmailField()
    def __str__(self):
        return self.user.get_full_name() or self.user.username

class Turno(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    especialidad = models.ForeignKey(Especialidad, on_delete=models.CASCADE)
    fecha = models.DateField()
    hora = models.TimeField()
    def __str__(self):
        return self.user.get_full_name()
    def clean(self):
        if Turno.objects.filter(doctor=self.doctor, fecha=self.fecha, hora=self.hora).exists():
            raise ValidationError('Ya existe un turno para ese doctor en esa fecha y hora.')
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    es_paciente = models.BooleanField(default=False)
    es_doctor = models.BooleanField(default=False)
    def __str__(self):
        return self.user.username
