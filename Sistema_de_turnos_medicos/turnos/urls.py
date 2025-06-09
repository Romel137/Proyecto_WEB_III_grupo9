from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('doctores/', views.listar_doctores, name='listar_doctores'),
    path('doctor/<int:pk>/', views.detalle_doctor, name='detalle_doctor'),
    path('turnos/', views.listar_turnos, name='listar_turnos'),
    path('turno/nuevo/', views.crear_turno, name='crear_turno'),
    path('registro/', views.registro, name='registro'),
    path('login/', views.iniciar_sesion, name='iniciar_sesion'),
    path('logout/', views.cerrar_sesion, name='cerrar_sesion'),
    path('mis-turnos/', views.mis_turnos, name='mis_turnos'),
    path('registro-doctor/', views.registrar_doctor, name='registro_doctor'),
    path('turno/<int:pk>/editar/', views.editar_turno, name='editar_turno'),
    path('turno/<int:pk>/eliminar/', views.eliminar_turno, name='eliminar_turno'),
]
