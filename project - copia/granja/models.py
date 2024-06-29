from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, date

class Trabajador(models.Model):
    ROLES = (
        ('administrador', 'Administrador'),
        ('trabajador', 'Trabajador'),
        ('veterinario', 'Veterinario'),
    )

    fecha_insert = models.DateField(auto_now_add=True)
    fecha_update = models.DateField(auto_now=True)
    name = models.TextField(max_length=50)
    cc = models.TextField(max_length=11)
    rol = models.CharField(max_length=20, choices=ROLES)
    direction = models.CharField(max_length=50)
    email = models.EmailField(blank=True)
    tel = models.TextField(max_length=11)
    fecha_registro = models.DateField(auto_now=True)

    encargado_insert = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='trabajador_creado', editable=False)
    encargado_update = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='trabajador_actualizado')

    def save(self, *args, **kwargs):
        # Antes de guardar un trabajador, se crea un usuario
        if not self.pk:
            # Usuario y contraseña iguales
            user = User.objects.create_user(username=self.cc, password=self.cc, first_name=self.name)
            user.save()
        else:
            # Si el trabajador ya existe, se actualiza el primer nombre 
            user = self.user
            if user:
                user.first_name = self.name
                user.save()

        super().save(*args, **kwargs)
    
    def __str__(self):
        texto = '{0} ({1})'
        return texto.format(self.name, self.rol)
    
class Animal(models.Model):
    SEXS = (
        ('macho', 'Macho'),
        ('hembra', 'Hembra'),
    )


    TYPES = (
        ('para leche', 'Para leche'),
        ('para venta', 'Para venta'),
        ('otro', 'Otro'),
    )
   
    HEALTHS = (
        ('saludable', 'Saludable'),
        ('enfermo', 'Enfermo'),
        ('otro', 'Otro'),
    )

    fecha_insert = models.DateField(auto_now_add=True)
    fecha_update = models.DateField(auto_now=True)
    num_id = models.CharField(max_length=50)
    birth = models.DateField()
    edad = models.CharField(max_length=50, blank=True)
    edad_categoria = models.CharField(max_length=20, blank=True)
    breed = models.TextField(max_length=50)
    color = models.TextField(max_length=50)
    sex = models.CharField(max_length=20, choices=SEXS)
    estado = models.TextField(default='en poseción', max_length=10)#el estado automatico sera "en posecion" al venderse sera "vendida"
    type = models.CharField(max_length=20, choices=TYPES)
    health = models.CharField(max_length=20, choices=HEALTHS)
    aditional = models.TextField(max_length=100)
    fecha_registro = models.DateField(auto_now=True)
    img_cow = models.ImageField(upload_to="media/cows/", null=True, blank=True)

    #peso = models.ForeignKey() conexion con los registros de salud
    encargado_insert = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='animal_creado', editable=False)
    encargado_update = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='animal_actualizado')
    
    def calcular_edad(self):
        fecha_actual = date.today()
        edad = fecha_actual - self.birth
        anios = edad.days // 365
        meses = (edad.days % 365) // 30
        dias = (edad.days % 365) % 30

        if meses == 0 and anios == 0:
            edad_formateada = f'{dias} dias.'
        elif anios == 0 and meses != 0:
            edad_formateada = f'{meses} meses.'
        else:
            edad_formateada = f'{anios} años, {meses} meses.'

        return edad_formateada
    
    def categoria_edad(self):
        edad = self.edad
        if 'meses' in edad and 'años' in edad:
            if self.sex == 'hembra':
                categoria = 'vaca'
            elif self.sex == 'macho':
                categoria = 'toro'
        else:
            categoria = 'ternero'
        return categoria
    
    def save(self, *args, **kwargs):
        self.edad = self.calcular_edad()
        self.edad_categoria = self.categoria_edad()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.breed} ({self.num_id})'
    
class Suministro(models.Model):
    TIPOS = (
        ('alimento', 'Alimento'),
        ('medicamento', 'Medicamento'),
        ('vacuna', 'Vacuna'),
        ('otro', 'Otro'),
    )

    CONDICIONES = (
        ('refrigerado', 'Refrigerado'),
        ('congelado', 'Congelado'),
        ('ambiente', 'Ambiente'),
        ('otro', 'Otro'),
    )

    fecha_insert = models.DateField(auto_now_add=True)
    fecha_update = models.DateField(auto_now=True)
    tipo = models.CharField(max_length=20, choices=TIPOS)
    name = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=100)
    cantidad = models.IntegerField()
    medida = models.CharField(max_length=10)
    lote = models.CharField(max_length=50)
    caducidad = models.DateField()
    condicion = models.CharField(max_length=20, choices=CONDICIONES)
    unidad = models.FloatField()
    total_actual = models.FloatField()
    total = models.FloatField(editable=False)

    encargado_insert = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='suministro_creado', editable=False)
    encargado_update = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='suministro_actualizado')

    def __str__(self):
        texto = '{0}, {1} ({2})'
        return texto.format(self.name, self.tipo, self.lote)
    
class Produccion(models.Model):
    TIPOS = (
        ('toro', 'Toro'),
        ('vaca', 'Vaca'),
        ('ternero', 'Ternero'),
    )

    fecha_insert = models.DateField(auto_now_add=True)
    fecha_update = models.DateField(auto_now=True)
    tipo = models.CharField(max_length=20)

    cantidad_leche = models.FloatField()
    vaca = models.CharField(max_length=50)

    tipo_ganado = models.CharField(max_length=20, choices=TIPOS)
    cantidad_vendidas = models.IntegerField()
    id_vendidas = models.CharField(max_length=100)
    precio = models.FloatField()

    adicional = models.CharField(max_length=100)

    encargado_insert = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='produccion_creado', editable=False)
    encargado_update = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='produccion_actualizada')

    def __str__(self):
        texto = '{0} ({1})'
        return texto.format(self.tipo, self.fecha_insert)
    
"""class Registro(models.Model):

    SIGNOS = (
        ('sí', 'Sí'),
        ('no', 'No'),
    )

    TIPOS = (
        ('inseminación artificial', 'Inseminación Artificial'),
        ('inseminación natural', 'Inseminación Natural'),
    )

    ESTADOS = (
        ('saludable', 'Saludable'),
        ('enferma', 'Enferma'),
    )

    fecha_insert = models.DateField(auto_now_add=True)
    fecha_update = models.DateField(auto_now=True)
    id_animal = models.CharField(max_length=20)
    tipo = models.CharField(max_length=20)

    # Descripcion para cada tipo que lo necesite
    descripcion = models.CharField(max_length=100)

    # Estado General
    general = models.CharField(max_length=2, choices=SIGNOS)

    # Vacunación
    nom_vacuna = models.CharField(max_length=20)

    # Tratamiento Médico
    nom_medicamento = models.CharField(max_length=20)
    razon = models.CharField(max_length=100)
    dosis = models.CharField(max_length=10)

    # Registro Peso
    peso = models.FloatField()

    # Registro inseminación
    tipo_inseminacion = models.CharField(max_length=20, choices=TIPOS)
    mat_genetico = models.CharField(max_length=20)

    # Registro Partos
    num_crias = models.IntegerField()
    estado = models.CharField(max_length=10, choices=ESTADOS)

    encargado_insert = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='produccion_creado', editable=False)
    encargado_update = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='produccion_actualizada')

    def __int__(self):
        texto = '{0} ({1})'
        return texto.format(self.id_animal, self.tipo)"""