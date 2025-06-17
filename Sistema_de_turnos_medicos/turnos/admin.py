from django.contrib import admin
from .models import Doctor, Paciente, Especialidad, Turno

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_nombre', 'get_apellido', 'especialidad']

    def get_nombre(self, obj):
        return obj.user.first_name
    get_nombre.short_description = 'Nombre'

    def get_apellido(self, obj):
        return obj.user.last_name
    get_apellido.short_description = 'Apellido'

    def get_email(self, obj):
        return obj.usuario.email
    get_email.short_description = 'Correo electrónico'

admin.site.register(Paciente)
admin.site.register(Especialidad)
admin.site.register(Turno)
