from django.contrib import admin
from .models import Doctor, Paciente, Especialidad, Turno

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('user', 'especialidad')
admin.site.register(Paciente)
admin.site.register(Especialidad)
admin.site.register(Turno)
