import os
import unicodedata

from django.core.management.base import BaseCommand

from wiki.models import Region

REGIONS = [
    {
        'name': 'Demacia',
        'short_code': 'DEM',
        'capital': 'Gran Demacia',
        'faction': 'Reino',
        'description': 'Demacia es un reino orgulloso y militarista que desprecia la magia, gobernado por valores de honor, orden y sacrificio.',
        'image_url': 'https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-clash/global/default/assets/images/background/background-demacia.jpg',
    },
    {
        'name': 'Noxus',
        'short_code': 'NOX',
        'capital': 'Bastión Inmortal',
        'faction': 'Imperio',
        'description': 'Noxus es un poderoso imperio expansionista que valora la fortaleza por encima de todo, sin importar el linaje ni el origen.',
        'image_url': 'https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-clash/global/default/assets/images/background/background-noxus.jpg',
    },
    {
        'name': 'Ionia',
        'short_code': 'ION',
        'capital': 'Placidium',
        'faction': 'Territorio mágico',
        'description': 'Ionia es una tierra de profunda espiritualidad y magia natural, compuesta por múltiples provincias con tradiciones únicas.',
        'image_url': 'https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-clash/global/default/assets/images/background/background-ionia.jpg',
    },
    {
        'name': 'Piltover',
        'short_code': 'PIL',
        'capital': 'Piltover',
        'faction': 'Ciudad estado',
        'description': 'Piltover es la ciudad del progreso tecnológico, donde la magitech florece y los inventores más brillantes de Runaterra trabajan.',
        'image_url': 'https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-clash/global/default/assets/images/background/background-piltover.jpg',
    },
    {
        'name': 'Zaun',
        'short_code': 'ZAU',
        'capital': 'Zaun',
        'faction': 'Ciudad estado',
        'description': 'Zaun es la ciudad subterránea bajo Piltover, marcada por la contaminación química, el ingenio callejero y la supervivencia.',
        'image_url': 'https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-clash/global/default/assets/images/background/background-zaun.jpg',
    },
    {
        'name': 'Freljord',
        'short_code': 'FRE',
        'capital': 'Ninguna fija',
        'faction': 'Tribu',
        'description': 'Freljord es una tierra helada de clanes enfrentados, profecías antiguas y guerras constantes por la supremacía entre tribus.',
        'image_url': 'https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-clash/global/default/assets/images/background/background-freljord.jpg',
    },
    {
        'name': 'Bilgewater',
        'short_code': 'BIL',
        'capital': 'Bilgewater',
        'faction': 'Ciudad estado',
        'description': 'Bilgewater es un puerto bullicioso y peligroso lleno de piratas, cazarrecompensas y criaturas del mar sin explorar.',
        'image_url': 'https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-clash/global/default/assets/images/background/background-bilgewater.jpg',
    },
    {
        'name': 'Shurima',
        'short_code': 'SHU',
        'capital': 'Shurima',
        'faction': 'Imperio',
        'description': 'Shurima es un desierto inmenso marcado por ruinas de un antiguo imperio, rituales de ascensión y guerras legendarias olvidadas.',
        'image_url': 'https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-clash/global/default/assets/images/background/background-shurima.jpg',
    },
    {
        'name': 'Islas Sombrías',
        'short_code': 'ISS',
        'capital': 'Ciudad Negra',
        'faction': 'Territorio mágico',
        'description': 'Las Islas Sombrías son una tierra maldita envuelta en niebla y muerte, donde los espíritus no encuentran descanso ni paz.',
        'image_url': 'https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-clash/global/default/assets/images/background/background-shadowisles.jpg',
    },
    {
        'name': 'El Vacío',
        'short_code': 'VAC',
        'capital': 'Ninguna',
        'faction': 'Territorio mágico',
        'description': 'El Vacío es una dimensión de corrupción y caos que busca devorar toda la vida y la magia existente en Runaterra.',
        'image_url': 'https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-clash/global/default/assets/images/background/background-void.jpg',
    },
]


def _ascii_name(name):
    normalized = unicodedata.normalize('NFD', name)
    return ''.join(c for c in normalized if unicodedata.category(c) != 'Mn')


class Command(BaseCommand):
    help = 'Seed the database with regions and verify local region images.'

    def handle(self, *args, **options):
        self._seed_regions()
        self._verify_images()

    def _seed_regions(self):
        self.stdout.write('Seeding regions...')
        for data in REGIONS:
            region, created = Region.objects.get_or_create(
                name=data['name'],
                defaults=data,
            )
            if created:
                self.stdout.write(f'  Created: {region.name}')
            else:
                self.stdout.write(f'  Already exists: {region.name}')
        self.stdout.write(self.style.SUCCESS(f'Done. {len(REGIONS)} regions processed.'))

    def _verify_images(self):
        img_dir = os.path.join('static', 'wiki', 'regions')
        missing = []
        for data in REGIONS:
            filename = _ascii_name(data['name']) + '.jpg'
            path = os.path.join(img_dir, filename)
            if os.path.exists(path):
                self.stdout.write(f'  OK: {filename}')
            else:
                missing.append(filename)
                self.stdout.write(self.style.WARNING(f'  Missing: {filename}'))
        if missing:
            self.stdout.write(self.style.WARNING(
                f'{len(missing)} image(s) missing. Place them in {img_dir}/'
            ))
        else:
            self.stdout.write(self.style.SUCCESS('All region images present.'))
