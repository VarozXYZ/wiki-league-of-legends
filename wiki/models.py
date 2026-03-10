import re
import unicodedata
from datetime import date

from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, MinValueValidator
from django.db import models
from django.templatetags.static import static


def validate_https_url(value):
    if value and not value.startswith('https://'):
        raise ValidationError('La URL debe empezar por https://')


def validate_uppercase_code(value):
    if value and value != value.upper():
        raise ValidationError('El código debe estar en mayúsculas.')


def validate_not_future_year(value):
    if value > date.today().year:
        raise ValidationError('El año no puede estar en el futuro.')


class Region(models.Model):
    FACTION_CHOICES = [
        ('Imperio', 'Imperio'),
        ('Reino', 'Reino'),
        ('Ciudad estado', 'Ciudad estado'),
        ('Tribu', 'Tribu'),
        ('Territorio mágico', 'Territorio mágico'),
    ]

    name = models.CharField(max_length=40, validators=[MinLengthValidator(3)])
    short_code = models.CharField(
        max_length=3,
        validators=[MinLengthValidator(2), validate_uppercase_code],
    )
    capital = models.CharField(max_length=40, validators=[MinLengthValidator(3)])
    faction = models.CharField(max_length=20, choices=FACTION_CHOICES)
    description = models.TextField(validators=[MinLengthValidator(40)])
    image_url = models.URLField(validators=[validate_https_url])

    @property
    def wiki_image_url(self):
        normalized = unicodedata.normalize('NFD', self.name)
        ascii_name = ''.join(c for c in normalized if unicodedata.category(c) != 'Mn')
        return static(f'wiki/regions/{ascii_name}.jpg')

    def __str__(self):
        return self.name


class Item(models.Model):
    TIER_CHOICES = [
        ('Inicial', 'Inicial'),
        ('Épico', 'Épico'),
        ('Legendario', 'Legendario'),
        ('Mítico', 'Mítico'),
    ]
    SLOT_CHOICES = [
        ('Daño', 'Daño'),
        ('Defensa', 'Defensa'),
        ('Utilidad', 'Utilidad'),
    ]

    name = models.CharField(max_length=60, validators=[MinLengthValidator(3)])
    tier = models.CharField(max_length=15, choices=TIER_CHOICES)
    slot_type = models.CharField(max_length=15, choices=SLOT_CHOICES)
    gold_cost = models.IntegerField(validators=[MinValueValidator(300)])
    description = models.TextField(validators=[MinLengthValidator(30)])
    image_url = models.URLField(validators=[validate_https_url])

    @property
    def wiki_image_url(self):
        clean = re.sub(r"[^a-zA-Z0-9 ]", '', self.name)
        return static(f'wiki/items/{clean}.png')

    def clean(self):
        super().clean()
        if self.tier == 'Mítico' and self.gold_cost < 2600:
            raise ValidationError(
                {'gold_cost': 'Un objeto mítico debe costar al menos 2600 de oro.'}
            )
        if self.tier == 'Legendario' and self.gold_cost < 2200:
            raise ValidationError(
                {'gold_cost': 'Un objeto legendario debe costar al menos 2200 de oro.'}
            )

    def __str__(self):
        return self.name


class Champion(models.Model):
    ROLE_CHOICES = [
        ('Asesino', 'Asesino'),
        ('Luchador', 'Luchador'),
        ('Mago', 'Mago'),
        ('Tirador', 'Tirador'),
        ('Soporte', 'Soporte'),
        ('Tanque', 'Tanque'),
    ]
    RESOURCE_CHOICES = [
        ('Mana', 'Mana'),
        ('Energía', 'Energía'),
        ('Furia', 'Furia'),
        ('Sin recurso', 'Sin recurso'),
    ]

    name = models.CharField(max_length=40, validators=[MinLengthValidator(2)])
    title = models.CharField(max_length=80, validators=[MinLengthValidator(4)])
    role = models.CharField(max_length=15, choices=ROLE_CHOICES)
    resource_type = models.CharField(max_length=15, choices=RESOURCE_CHOICES)
    release_year = models.IntegerField(
        validators=[MinValueValidator(2009), validate_not_future_year]
    )
    lore = models.TextField(validators=[MinLengthValidator(60)])
    image_url = models.URLField(validators=[validate_https_url])
    regions = models.ManyToManyField(Region, related_name='champions')
    featured_items = models.ManyToManyField(Item, related_name='champions', blank=True)

    def clean(self):
        super().clean()
        if self.role == 'Tirador' and self.resource_type == 'Furia':
            raise ValidationError(
                {'resource_type': 'Los tiradores de esta wiki no pueden usar furia.'}
            )

    @property
    def wiki_square_image_url(self):
        return static(f'wiki/champions/{self.name}.png')

    def __str__(self):
        return f'{self.name} - {self.title}'
