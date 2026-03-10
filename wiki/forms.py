from django import forms

from wiki.models import Champion, Item, Region


class RegionForm(forms.ModelForm):
    class Meta:
        model = Region
        fields = '__all__'
        labels = {
            'name': 'Nombre',
            'short_code': 'Codigo corto',
            'capital': 'Capital',
            'faction': 'Tipo de faccion',
            'description': 'Descripcion',
            'image_url': 'URL de imagen',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }
        error_messages = {
            'name': {
                'required': 'Debes indicar el nombre de la región.',
                'min_length': 'El nombre de la región debe tener al menos %(limit_value)d caracteres.',
                'max_length': 'El nombre de la región no puede superar %(limit_value)d caracteres.',
            },
            'short_code': {
                'required': 'Debes indicar un código corto.',
                'min_length': 'El código debe tener al menos %(limit_value)d caracteres.',
                'max_length': 'El código no puede superar %(limit_value)d caracteres.',
            },
            'image_url': {
                'required': 'Debes indicar una imagen para la región.',
            },
        }


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = '__all__'
        labels = {
            'name': 'Nombre',
            'tier': 'Tier',
            'slot_type': 'Tipo de objeto',
            'gold_cost': 'Coste en oro',
            'description': 'Descripcion',
            'image_url': 'URL de imagen',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }
        error_messages = {
            'name': {
                'required': 'Debes indicar el nombre del objeto.',
                'min_length': 'El nombre del objeto debe tener al menos %(limit_value)d caracteres.',
                'max_length': 'El nombre del objeto no puede superar %(limit_value)d caracteres.',
            },
            'gold_cost': {
                'required': 'Debes indicar el coste en oro.',
                'min_value': 'El coste mínimo permitido es %(limit_value)d.',
            },
            'image_url': {
                'required': 'Debes indicar una imagen para el objeto.',
            },
        }


class ChampionForm(forms.ModelForm):
    class Meta:
        model = Champion
        fields = '__all__'
        labels = {
            'name': 'Nombre',
            'title': 'Titulo',
            'role': 'Rol',
            'resource_type': 'Tipo de recurso',
            'release_year': 'Ano de lanzamiento',
            'lore': 'Lore',
            'image_url': 'URL de imagen',
            'regions': 'Regiones',
            'featured_items': 'Objetos destacados',
        }
        help_texts = {
            'regions': 'Mantén Ctrl o Cmd para seleccionar varias regiones.',
            'featured_items': 'Mantén Ctrl o Cmd para seleccionar varios objetos.',
        }
        widgets = {
            'lore': forms.Textarea(attrs={'rows': 6}),
            'regions': forms.SelectMultiple(attrs={'size': 5}),
            'featured_items': forms.SelectMultiple(attrs={'size': 6}),
        }
        error_messages = {
            'name': {
                'required': 'Debes indicar el nombre del campeón.',
                'min_length': 'El nombre del campeón debe tener al menos %(limit_value)d caracteres.',
                'max_length': 'El nombre del campeón no puede superar %(limit_value)d caracteres.',
            },
            'title': {
                'required': 'Debes indicar el título del campeón.',
                'min_length': 'El título debe tener al menos %(limit_value)d caracteres.',
                'max_length': 'El título no puede superar %(limit_value)d caracteres.',
            },
            'regions': {
                'required': 'Debes asignar al menos una región.',
            },
            'image_url': {
                'required': 'Debes indicar una imagen para el campeón.',
            },
        }
