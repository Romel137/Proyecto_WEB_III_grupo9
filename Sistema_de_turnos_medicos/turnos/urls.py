from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('doctores/', views.listar_doctores, name='listar_doctores'),
    path('doctor/<int:pk>/', views.detalle_doctor, name='detalle_doctor'),
    path('turnos/', views.listar_turnos, name='listar_turnos'),
    path('registro/', views.registro, name='registro'),
    path('login/', views.iniciar_sesion, name='iniciar_sesion'),
    path('logout/', views.cerrar_sesion, name='cerrar_sesion'),
    path('mis-turnos/', views.mis_turnos, name='mis_turnos'),
    path('registro-doctor/', views.registrar_doctor, name='registro_doctor'),
    path('crear-especialidad/', views.crear_especialidad, name='crear_especialidad'),
    path('crear-ficha/', views.crear_ficha, name='crear_ficha'),

    path('reservar-ficha/<int:turno_id>/', views.reservar_ficha, name='reservar_ficha'),
    path('sugerir-turno/<int:doctor_id>/', views.sugerir_turno, name='sugerir_turno'),
    
    path('ajax/doctores/', views.obtener_doctores_por_especialidad, name='obtener_doctores'),

    
    path('crear-ficha/', views.crear_ficha, name='crear_ficha'),
    path('reservar/<int:turno_id>/', views.reservar_ficha, name='reservar_turno'),
    path('cancelar/<int:turno_id>/', views.cancelar_turno, name='cancelar_turno'),
    path('reservar_turno/<int:turno_id>/', views.reservar_ficha, name='reservar_turno'),
    path('sugerir-turno/<int:doctor_id>/', views.sugerir_turno, name='sugerir_turno'),

    #path('elegir-doctor/', views.elegir_doctor, name='elegir_doctor'),

    
    
    
]
