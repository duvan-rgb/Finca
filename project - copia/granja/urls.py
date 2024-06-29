from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.log_out, name='logout'),

    # ADMINISTRADOR
    path('administrador/', views.administrador, name='administrador'),

    # ADMINISTRADOR-ANIMALES
    path('administrador/animales/', views.animals, name='animals'),
    path('administrador/animales/insert/', views.insert_animal, name='insert_animal'),
    path('administrador/animales/reload-edad/', views.update_edad, name='update_edad'),
    path('administrador/animales/update/', views.update_animal, name='update_animal'),
    path('administrador/animales/update/<int:animal_id>/', views.update_form_animal, name='update_form_animal'),
    path('administrador/animales/delete/<int:animal_id>/', views.delete_animal, name='delete_animal'),
    path('administrador/animales/search', views.lista_animales, name='lista_animales'),

    # ADMINISTRADOR-TRABAJADORES
    path('administrador/trabajadores/', views.workers, name='workers'),
    path('administrador/trabajadores/insert/', views.insert_worker, name='insert_worker'),
    path('administrador/trabajadores/update/', views.update_worker, name='update_worker'),
    path('administrador/trabajadores/update/<int:worker_id>/', views.update_form_worker, name='update_form_worker'),
    path('administrador/trabajadores/delete/<int:worker_id>/', views.delete_worker, name='delete_worker'),
    path('administrador/trabajadores/search', views.lista_trabajadores, name='lista_trabajadores'),

    # ADMINISTRADOR-SUMINISTROS
    path('administrador/suministros/', views.supplies, name='supplies'),
    path('administrador/suministros/insert/', views.insert_supplie, name='insert_supplie'),
    path('administrador/suministros/update-cantidad/', views.update_cantidad, name='update_cantidad'),
    path('administrador/suministros/update/', views.update_supplie, name='update_supplie'),
    path('administrador/suministros/update/<int:suministro_id>/', views.update_form_supplie, name='update_form_supplie'),
    path('administrador/suministros/delete/<int:suministro_id>/', views.delete_supplie, name='delete_supplie'),
    path('administrador/suministros/search/', views.lista_suministros, name='lista_suministros'),

    path('administrador/suministros/grafico-precios/', views.grafico_precio, name='grafico_precio'),
    path('administrador/suministros/grafico-existencias/', views.grafico_existencias, name='grafico_existencias'),

    # ADMINISTRADOR-PRODUCCION
    path('administrador/produccion/', views.production, name='production'),
    path('administrador/produccion/insert/', views.insert_production, name='insert_production'),
    path('administrador/produccion/delete/<int:produccion_id>/', views.delete_production, name='delete_production'),

    # ADMINISTRADOR-REGISTROS DE SALUD
    path('administrador/registros-salud/', views.record, name='record'),

    # TRABAJADOR
    path('trabajador/', views.worker, name='worker'),

    # TRABAJADOR-ANIMALES
    path('trabajador/animales/', views.animals2, name='animals2'),

    # TRABAJADOR-SUMINISTROS
    path('trabajador/suministros/', views.supplies2, name='supplies2'),

    # TRABAJADOR-PRODUCCION
    path('trabajador/produccion/', views.production2, name='production2'),

    # VETERINARIO
    path('veterinario/', views.vet, name='vet'),

    # VETERINARIO-REGISTROS DE SALUD
    path('veterinario/registros-salud/', views.record2, name='record2'),
    
    # GRAFICO AUTOMATICO
    path('get-chart/', views.get_chart, name='get_chart'),
]