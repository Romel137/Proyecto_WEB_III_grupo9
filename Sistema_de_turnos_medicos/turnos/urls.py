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

   
    path('sugerir-turno/<int:doctor_id>/', views.sugerir_turno, name='sugerir_turno'),
    
    path('ajax/doctores/', views.obtener_doctores_por_especialidad, name='obtener_doctores'),


    path('reservar/', views.reservar_ficha, name='reservar_ficha'),
    path('reservar/<int:turno_id>/', views.confirmar_reserva, name='confirmar_reserva'),

    
    path('crear-ficha/', views.crear_ficha, name='crear_ficha'),
    
    path('cancelar/<int:turno_id>/', views.cancelar_turno, name='cancelar_turno'),
    
    path('turno/reservar/<int:turno_id>/', views.reservar_ficha_confirmar, name='reservar_ficha_confirmar'),

    
    path('reservar_turno/<int:turno_id>/', views.reservar_ficha, name='reservar_turno'),
    path('sugerir-turno/<int:doctor_id>/', views.sugerir_turno, name='sugerir_turno'),

    #path('elegir-doctor/', views.elegir_doctor, name='elegir_doctor'),

    
    
    
]
