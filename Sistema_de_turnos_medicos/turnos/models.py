from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Especialidad(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.nombre

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    especialidad = models.ForeignKey(Especialidad, on_delete=models.CASCADE, related_name='doctors')
    def __str__(self):
        return f"Dr. {self.user.first_name} {self.user.last_name} ({self.especialidad.nombre})"

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
    def clean(self):
        if not self.doctor_id or not self.fecha or not self.hora:
            return
        if Turno.objects.filter(doctor=self.doctor, fecha=self.fecha, hora=self.hora).exists():
            raise ValidationError("Ya existe un turno con ese doctor, fecha y hora.")
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.doctor.user.get_full_name()} - {self.fecha} {self.hora}"

class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    es_paciente = models.BooleanField(default=False)
    es_doctor = models.BooleanField(default=False)
    def __str__(self):
        return self.user.username
