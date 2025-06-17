from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone


class Especialidad(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre


class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    especialidad = models.ForeignKey('Especialidad', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.get_full_name()} ({self.especialidad})'


class Paciente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telefono = models.CharField(max_length=20)
    email = models.EmailField()

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Turno(models.Model):
    paciente = models.ForeignKey('Paciente', on_delete=models.CASCADE, null=True, blank=True)
    doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE)
    especialidad = models.ForeignKey('Especialidad', on_delete=models.CASCADE)
    fecha = models.DateField()
    hora = models.TimeField()
    reservado = models.BooleanField(default=False)
    recordatorio_enviado = models.BooleanField(default=False)

    class Meta:
        ordering = ['fecha', 'hora']
        unique_together = ('doctor', 'fecha', 'hora')

    def __str__(self):
        return f"{self.doctor.user.get_full_name()} - {self.fecha} {self.hora}"

    def clean(self):
        if not self.doctor_id or not self.fecha or not self.hora:
            return

        # Evita duplicados (excepto a sí mismo)
        conflicto = Turno.objects.filter(
            doctor=self.doctor,
            fecha=self.fecha,
            hora=self.hora
        ).exclude(pk=self.pk).exists()

        if conflicto:
            raise ValidationError("Ya existe un turno con ese doctor, fecha y hora.")

        # Reglas lógico-consistentes
        if self.reservado and self.paciente is None:
            raise ValidationError("Un turno reservado debe tener un paciente.")
        if not self.reservado and self.paciente is not None:
            raise ValidationError("Un turno no reservado no puede tener un paciente.")

        # Evita turnos en el pasado
        fecha_hora = timezone.make_aware(
            timezone.datetime.combine(self.fecha, self.hora)
        )
        if fecha_hora < timezone.now():
            raise ValidationError("No se pueden asignar turnos en el pasado.")

    @property
    def disponible(self):
        """Retorna True si el turno está libre para ser reservado"""
        return not self.reservado and self.paciente is None

    def reservar(self, paciente):
        """Asigna el paciente y marca como reservado"""
        if not self.disponible:
            raise ValidationError("Este turno ya está reservado.")
        self.paciente = paciente
        self.reservado = True
        self.full_clean()
        self.save()

    def cancelar(self):
        """Cancela el turno: lo libera del paciente"""
        if not self.reservado or not self.paciente:
            raise ValidationError("Este turno no está reservado.")
        self.paciente = None
        self.reservado = False
        self.full_clean()
        self.save()


class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    es_paciente = models.BooleanField(default=False)
    es_doctor = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
