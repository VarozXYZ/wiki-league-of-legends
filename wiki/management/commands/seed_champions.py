import os

from django.core.management.base import BaseCommand

from wiki.models import Champion, Region

REGIONS = [
    {
        'name': 'Demacia',
        'short_code': 'DEM',
        'capital': 'Gran Demacia',
        'faction': 'Reino',
        'description': 'Demacia es un reino orgulloso y militarista que desprecia la magia, gobernado por valores de honor, orden y sacrificio.',
        'image_url': 'https://example.com/demacia.jpg',
    },
    {
        'name': 'Noxus',
        'short_code': 'NOX',
        'capital': 'Bastión Inmortal',
        'faction': 'Imperio',
        'description': 'Noxus es un poderoso imperio expansionista que valora la fortaleza por encima de todo, sin importar el linaje ni el origen.',
        'image_url': 'https://example.com/noxus.jpg',
    },
    {
        'name': 'Ionia',
        'short_code': 'ION',
        'capital': 'Placidium',
        'faction': 'Territorio mágico',
        'description': 'Ionia es una tierra de profunda espiritualidad y magia natural, compuesta por múltiples provincias con tradiciones únicas.',
        'image_url': 'https://example.com/ionia.jpg',
    },
    {
        'name': 'Piltover',
        'short_code': 'PIL',
        'capital': 'Piltover',
        'faction': 'Ciudad estado',
        'description': 'Piltover es la ciudad del progreso tecnológico, donde la magitech florece y los inventores más brillantes de Runaterra trabajan.',
        'image_url': 'https://example.com/piltover.jpg',
    },
    {
        'name': 'Zaun',
        'short_code': 'ZAU',
        'capital': 'Zaun',
        'faction': 'Ciudad estado',
        'description': 'Zaun es la ciudad subterránea bajo Piltover, marcada por la contaminación química, el ingenio callejero y la supervivencia.',
        'image_url': 'https://example.com/zaun.jpg',
    },
    {
        'name': 'Freljord',
        'short_code': 'FRE',
        'capital': 'Ninguna fija',
        'faction': 'Tribu',
        'description': 'Freljord es una tierra helada de clanes enfrentados, profecías antiguas y guerras constantes por la supremacía entre tribus.',
        'image_url': 'https://example.com/freljord.jpg',
    },
    {
        'name': 'Bilgewater',
        'short_code': 'BIL',
        'capital': 'Bilgewater',
        'faction': 'Ciudad estado',
        'description': 'Bilgewater es un puerto bullicioso y peligroso lleno de piratas, cazarrecompensas y criaturas del mar sin explorar.',
        'image_url': 'https://example.com/bilgewater.jpg',
    },
    {
        'name': 'Shurima',
        'short_code': 'SHU',
        'capital': 'Shurima',
        'faction': 'Imperio',
        'description': 'Shurima es un desierto inmenso marcado por ruinas de un antiguo impero, rituales de ascensión y guerras legendarias olvidadas.',
        'image_url': 'https://example.com/shurima.jpg',
    },
    {
        'name': 'Islas Sombrías',
        'short_code': 'ISS',
        'capital': 'Ciudad Negra',
        'faction': 'Territorio mágico',
        'description': 'Las Islas Sombrías son una tierra maldita envuelta en niebla y muerte, donde los espíritus no encuentran descanso ni paz.',
        'image_url': 'https://example.com/shadowisles.jpg',
    },
    {
        'name': 'El Vacío',
        'short_code': 'VAC',
        'capital': 'Ninguna',
        'faction': 'Territorio mágico',
        'description': 'El Vacío es una dimensión de corrupción y caos que busca devorar toda la vida y la magia existente en Runaterra.',
        'image_url': 'https://example.com/void.jpg',
    },
]

CHAMPIONS = [
    {
        'name': 'Jinx',
        'title': 'La Sueltalocas',
        'role': 'Tirador',
        'resource_type': 'Mana',
        'release_year': 2013,
        'lore': 'Jinx es una criminal anarquista de Zaun que siembra el caos por pura diversión, armada con un arsenal devastador y sin miedo alguno a las consecuencias.',
        'image_url': 'https://example.com/jinx.jpg',
        'regions': ['Zaun'],
    },
    {
        'name': 'Thresh',
        'title': 'El Carcelero de Cadenas',
        'role': 'Soporte',
        'resource_type': 'Mana',
        'release_year': 2013,
        'lore': 'Thresh es un espíritu sádico de las Islas Sombrías que colecciona almas en su linterna, disfrutando de la tortura psicológica de sus víctimas.',
        'image_url': 'https://example.com/thresh.jpg',
        'regions': ['Islas Sombrías'],
    },
    {
        'name': 'Zed',
        'title': 'El Maestro de las Sombras',
        'role': 'Asesino',
        'resource_type': 'Energía',
        'release_year': 2012,
        'lore': 'Zed es un maestro ninja que desafió las enseñanzas de su orden al dominar la magia prohibida de las sombras para salvar a Ionia de Noxus.',
        'image_url': 'https://example.com/zed.jpg',
        'regions': ['Ionia'],
    },
    {
        'name': 'Jhin',
        'title': 'El Virtuoso',
        'role': 'Tirador',
        'resource_type': 'Mana',
        'release_year': 2016,
        'lore': 'Jhin es un asesino psicótico de Ionia que concibe sus crímenes como obras de arte, ejecutando cada asesinato con una precisión meticulosa y teatral.',
        'image_url': 'https://example.com/jhin.jpg',
        'regions': ['Ionia'],
    },
    {
        'name': 'Ekko',
        'title': 'El Chico que Rompió el Tiempo',
        'role': 'Asesino',
        'resource_type': 'Mana',
        'release_year': 2015,
        'lore': 'Ekko es un joven genio de Zaun que inventó un dispositivo capaz de manipular el tiempo para proteger a sus amigos y desafiar a los poderosos.',
        'image_url': 'https://example.com/ekko.jpg',
        'regions': ['Zaun'],
    },
    {
        'name': 'Miss Fortune',
        'title': 'La Cazarrecompensas',
        'role': 'Tirador',
        'resource_type': 'Mana',
        'release_year': 2010,
        'lore': 'Miss Fortune es una cazarrecompensas de Bilgewater que persigue al asesino de su madre, moviéndose por las sombras del puerto con dos pistolas y sed de venganza.',
        'image_url': 'https://example.com/mf.jpg',
        'regions': ['Bilgewater'],
    },
    {
        'name': 'Katarina',
        'title': 'La Asesina Sinuosa',
        'role': 'Asesino',
        'resource_type': 'Sin recurso',
        'release_year': 2009,
        'lore': 'Katarina es la asesina más temida de Noxus, heredera del clan Du Couteau, conocida por su velocidad letal y su absoluta fidelidad al imperio.',
        'image_url': 'https://example.com/katarina.jpg',
        'regions': ['Noxus'],
    },
    {
        'name': 'Darius',
        'title': 'La Mano de Noxus',
        'role': 'Luchador',
        'resource_type': 'Sin recurso',
        'release_year': 2012,
        'lore': 'Darius es el comandante más implacable del ejército noxiano, que se alzó desde la miseria hasta convertirse en el símbolo viviente del poder de Noxus.',
        'image_url': 'https://example.com/darius.jpg',
        'regions': ['Noxus'],
    },
    {
        'name': 'Leona',
        'title': 'La Aurora Radiante',
        'role': 'Tanque',
        'resource_type': 'Mana',
        'release_year': 2011,
        'lore': 'Leona es una guerrera Solari de las montañas de Demacia que canaliza el poder del sol a través de su escudo y espada para proteger a los inocentes.',
        'image_url': 'https://example.com/leona.jpg',
        'regions': ['Demacia'],
    },
    {
        'name': 'Morgana',
        'title': 'La Caída de los Ángeles',
        'role': 'Soporte',
        'resource_type': 'Mana',
        'release_year': 2009,
        'lore': 'Morgana es un ángel caído que rechazó el destino de su hermana y eligió abrazar la oscuridad para comprender el sufrimiento de los mortales.',
        'image_url': 'https://example.com/morgana.jpg',
        'regions': ['Demacia'],
    },
    {
        'name': 'Ezreal',
        'title': 'El Explorador Prodigioso',
        'role': 'Tirador',
        'resource_type': 'Mana',
        'release_year': 2010,
        'lore': 'Ezreal es un joven explorador de Piltover con un talento innato para la magia, famoso por sus expediciones a ruinas antiguas en busca de reliquias perdidas.',
        'image_url': 'https://example.com/ezreal.jpg',
        'regions': ['Piltover'],
    },
    {
        'name': 'Vi',
        'title': 'La Ejecutora de Piltover',
        'role': 'Luchador',
        'resource_type': 'Mana',
        'release_year': 2012,
        'lore': 'Vi es una ex ladrona de Zaun que se convirtió en oficial de la Guardia Piltover, conocida por resolver todos sus problemas a base de puñetazos devastadores.',
        'image_url': 'https://example.com/vi.jpg',
        'regions': ['Piltover', 'Zaun'],
    },
    {
        'name': 'Twisted Fate',
        'title': 'El Maestro de Cartas',
        'role': 'Mago',
        'resource_type': 'Mana',
        'release_year': 2009,
        'lore': 'Twisted Fate es un estafador y jugador de Bilgewater con poderes mágicos sobre las cartas, siempre un paso por delante de quienes intentan atraparle.',
        'image_url': 'https://example.com/tf.jpg',
        'regions': ['Bilgewater'],
    },
    {
        'name': 'Sivir',
        'title': 'La Guerrera de Batalla',
        'role': 'Tirador',
        'resource_type': 'Mana',
        'release_year': 2009,
        'lore': 'Sivir es una mercenaria de Shurima experta en el combate con cuchillas, descendiente de la línea de Azir, cuyo destino está atado al antiguo imperio.',
        'image_url': 'https://example.com/sivir.jpg',
        'regions': ['Shurima'],
    },
    {
        'name': 'Syndra',
        'title': 'La Soberana Oscura',
        'role': 'Mago',
        'resource_type': 'Mana',
        'release_year': 2012,
        'lore': 'Syndra es una maga de Ionia de poder ilimitado que fue encadenada por sus maestros por miedo, y que ahora busca destruir las cadenas que la aprisionaron.',
        'image_url': 'https://example.com/syndra.jpg',
        'regions': ['Ionia'],
    },
    {
        'name': 'Draven',
        'title': 'El Glorioso Ejecutor',
        'role': 'Tirador',
        'resource_type': 'Mana',
        'release_year': 2012,
        'lore': 'Draven es un ejecutor noxiano que convirtió la muerte en un espectáculo, cazando fama y adoración del público con hacha en mano y ego desmesurado.',
        'image_url': 'https://example.com/draven.jpg',
        'regions': ['Noxus'],
    },
    {
        'name': 'Ashe',
        'title': 'La Reina Flecha de Hielo',
        'role': 'Tirador',
        'resource_type': 'Mana',
        'release_year': 2009,
        'lore': 'Ashe es la reina guerrera de la tribu Avarosa en el Freljord, que usa su arco encantado para unir a los clanes y guiar a su pueblo hacia la paz.',
        'image_url': 'https://example.com/ashe.jpg',
        'regions': ['Freljord'],
    },
    {
        'name': 'Vel\'Koz',
        'title': 'El Ojo del Vacío',
        'role': 'Mago',
        'resource_type': 'Mana',
        'release_year': 2014,
        'lore': "Vel'Koz es una entidad del Vacío que destruye todo lo que investiga en busca de conocimiento absoluto, diseccionando la realidad con sus rayos devastadores.",
        'image_url': 'https://example.com/velkoz.jpg',
        'regions': ['El Vacío'],
    },
    {
        'name': 'Nautilus',
        'title': 'El Titán de las Profundidades',
        'role': 'Tanque',
        'resource_type': 'Mana',
        'release_year': 2012,
        'lore': 'Nautilus es un marinero de Bilgewater abandonado en el fondo del océano que fue absorbido por una oscuridad abismal y convertido en un guardián eterno.',
        'image_url': 'https://example.com/nautilus.jpg',
        'regions': ['Bilgewater'],
    },
    {
        'name': 'Zyra',
        'title': 'Surgida de las Espinas',
        'role': 'Mago',
        'resource_type': 'Mana',
        'release_year': 2012,
        'lore': 'Zyra es una antigua planta carnívora que tomó forma humana al absorber el alma de una maga moribunda, usando ahora ese cuerpo para expandir su reino vegetal.',
        'image_url': 'https://example.com/zyra.jpg',
        'regions': ['Shurima'],
    },
]


class Command(BaseCommand):
    help = 'Seed the database with regions and champions, and download champion images.'

    def handle(self, *args, **options):
        self._seed_regions()
        self._seed_champions()
        self._download_images()

    def _seed_regions(self):
        for data in REGIONS:
            region, created = Region.objects.get_or_create(
                name=data['name'],
                defaults=data,
            )
            if created:
                self.stdout.write(f'  Region created: {region.name}')

    def _seed_champions(self):
        for data in CHAMPIONS:
            region_names = data.pop('regions')
            champion, created = Champion.objects.get_or_create(
                name=data['name'],
                defaults=data,
            )
            if created:
                for region_name in region_names:
                    try:
                        region = Region.objects.get(name=region_name)
                        champion.regions.add(region)
                    except Region.DoesNotExist:
                        self.stdout.write(self.style.WARNING(f'    Region not found: {region_name}'))
                self.stdout.write(f'  Champion created: {champion.name}')
            # Restore the key for potential re-runs
            data['regions'] = region_names

    def _download_images(self):
        try:
            import requests
        except ImportError:
            self.stdout.write(self.style.WARNING('requests not installed, skipping image download.'))
            return

        out_dir = os.path.join('static', 'wiki', 'champions')
        os.makedirs(out_dir, exist_ok=True)

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        base = 'https://raw.communitydragon.org/latest'

        self.stdout.write('Fetching champion ID list from CommunityDragon...')
        try:
            r = requests.get(
                f'{base}/plugins/rcp-be-lol-game-data/global/default/v1/champion-summary.json',
                headers=headers,
                timeout=30,
            )
            r.raise_for_status()
            summary = r.json()
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Could not fetch champion list: {e}'))
            return

        # Build a lookup: lowercase name → id
        id_map = {c['name'].lower(): c['id'] for c in summary}

        champion_names = list(Champion.objects.values_list('name', flat=True))
        for name in champion_names:
            dest = os.path.join(out_dir, f'{name}.png')
            if os.path.exists(dest):
                continue

            champ_id = id_map.get(name.lower())
            if champ_id is None:
                self.stdout.write(self.style.WARNING(f'  No ID found for: {name}'))
                continue

            url = f'{base}/plugins/rcp-be-lol-game-data/global/default/v1/champion-icons/{champ_id}.png'
            try:
                resp = requests.get(url, headers=headers, timeout=30)
                resp.raise_for_status()
                with open(dest, 'wb') as f:
                    f.write(resp.content)
                self.stdout.write(f'  Downloaded: {name}.png ({len(resp.content)} bytes)')
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'  Failed {name}: {e}'))

        self.stdout.write(self.style.SUCCESS('Done.'))
