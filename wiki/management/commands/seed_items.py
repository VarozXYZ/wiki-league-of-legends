import os
import re

from django.core.management.base import BaseCommand

from wiki.models import Item

ITEMS = [
    # ── Inicial ────────────────────────────────────────────────────────────────
    {
        'name': "Doran's Blade",
        'tier': 'Inicial',
        'slot_type': 'Daño',
        'gold_cost': 450,
        'description': "Espada de inicio que otorga daño de ataque, vida y vampirismo para sostenerse en la botlane durante las primeras fases del juego.",
        'image_url': 'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/assets/items/icons2d/1055_marksman_t1_doransblade.png',
    },
    {
        'name': "Doran's Ring",
        'tier': 'Inicial',
        'slot_type': 'Daño',
        'gold_cost': 400,
        'description': "Anillo de inicio que aporta poder de habilidad, vida y regeneración de maná, ideal para magos que necesitan aguantar en la fase de línea.",
        'image_url': 'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/assets/items/icons2d/1056_mage_t1_doransring.png',
    },
    {
        'name': "Doran's Shield",
        'tier': 'Inicial',
        'slot_type': 'Defensa',
        'gold_cost': 450,
        'description': "Escudo de inicio que otorga vida, regeneración y reducción de daño básico entrante, perfecto para tanques y luchadores en early game.",
        'image_url': 'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/assets/items/icons2d/1054_tank_t1_doransshield.png',
    },
    # ── Épico ──────────────────────────────────────────────────────────────────
    {
        'name': 'Long Sword',
        'tier': 'Épico',
        'slot_type': 'Daño',
        'gold_cost': 350,
        'description': "Componente básico de daño de ataque que entra en la construcción de multitud de objetos ofensivos a lo largo del juego.",
        'image_url': 'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/assets/items/icons2d/1036_class_t1_longsword.png',
    },
    {
        'name': 'Pickaxe',
        'tier': 'Épico',
        'slot_type': 'Daño',
        'gold_cost': 875,
        'description': "Componente de daño de ataque intermedio que forma parte de los objetos más poderosos del arsenal físico en Runaterra.",
        'image_url': 'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/assets/items/icons2d/1037_class_t1_pickaxe.png',
    },
    {
        'name': 'B.F. Sword',
        'tier': 'Épico',
        'slot_type': 'Daño',
        'gold_cost': 1300,
        'description': "Gran espada que representa el componente de daño de ataque más costoso del juego, base de objetos míticos y legendarios muy poderosos.",
        'image_url': 'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/assets/items/icons2d/1038_class_t1_bfsword.png',
    },
    {
        'name': 'Cloth Armor',
        'tier': 'Épico',
        'slot_type': 'Defensa',
        'gold_cost': 300,
        'description': "Componente de armadura básico que proporciona defensa física mínima y entra en la construcción de decenas de objetos defensivos.",
        'image_url': 'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/assets/items/icons2d/1029_base_t1_clotharmor.png',
    },
    {
        'name': 'Chain Vest',
        'tier': 'Épico',
        'slot_type': 'Defensa',
        'gold_cost': 800,
        'description': "Chaleco de malla que otorga una cantidad considerable de armadura, usado como componente base para objetos defensivos de alto nivel.",
        'image_url': 'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/assets/items/icons2d/1031_base_t2_chainvest.png',
    },
    {
        'name': 'Amplifying Tome',
        'tier': 'Épico',
        'slot_type': 'Daño',
        'gold_cost': 435,
        'description': "Tomo mágico que incrementa el poder de habilidad del portador, siendo el componente esencial de casi todos los objetos de daño mágico.",
        'image_url': 'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/assets/items/icons2d/1052_mage_t2_amptome.png',
    },
    {
        'name': 'Needlessly Large Rod',
        'tier': 'Épico',
        'slot_type': 'Daño',
        'gold_cost': 1250,
        'description': "Vara excesivamente grande y repleta de energía mágica que proporciona una enorme cantidad de poder de habilidad a cualquier mago.",
        'image_url': 'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/assets/items/icons2d/1058_mage_t1_largerod.png',
    },
    {
        'name': "Caulfield's Warhammer",
        'tier': 'Épico',
        'slot_type': 'Daño',
        'gold_cost': 1100,
        'description': "Martillo de guerra que combina daño de ataque y reducción de enfriamiento, siendo base de muchos objetos de asesino y luchador.",
        'image_url': 'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/assets/items/icons2d/3133_fighter_t2_caulfieldswarhammer.png',
    },
    {
        'name': 'Lost Chapter',
        'tier': 'Épico',
        'slot_type': 'Daño',
        'gold_cost': 1300,
        'description': "Libro mágico que otorga poder de habilidad y maná, restaurando además parte del maná perdido cada vez que el portador sube de nivel.",
        'image_url': 'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/assets/items/icons2d/3802_mage_tier2_lostchapter.png',
    },
    # ── Legendario ─────────────────────────────────────────────────────────────
    {
        'name': 'Infinity Edge',
        'tier': 'Legendario',
        'slot_type': 'Daño',
        'gold_cost': 3400,
        'description': "El objeto de daño físico más icónico del juego. Amplifica el daño crítico de forma masiva para los tiradores que buscan máxima devastación.",
        'image_url': 'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/assets/items/icons2d/3031_marksman_t3_infinityedge.png',
    },
    {
        'name': "Rabadon's Deathcap",
        'tier': 'Legendario',
        'slot_type': 'Daño',
        'gold_cost': 3800,
        'description': "Sombrero que amplifica todo el poder de habilidad del portador en un enorme porcentaje, siendo el objeto de mago definitivo en el juego.",
        'image_url': 'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/assets/items/icons2d/3089_mage_t3_deathcap.png',
    },
    {
        'name': "Zhonya's Hourglass",
        'tier': 'Legendario',
        'slot_type': 'Daño',
        'gold_cost': 2600,
        'description': "Reloj de arena que pone al portador en estado de invulnerabilidad al activarse, salvando vidas en los momentos más críticos del combate.",
        'image_url': 'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/assets/items/icons2d/3157_mage_t3_zhonyashourglass.png',
    },
    {
        'name': 'Mortal Reminder',
        'tier': 'Legendario',
        'slot_type': 'Daño',
        'gold_cost': 2500,
        'description': "Espada que aplica heridas graves al objetivo, reduciendo drásticamente la curación recibida por los enemigos físicamente atacados.",
        'image_url': 'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/assets/items/icons2d/3033_marksman_t3_mortalreminder.png',
    },
    {
        'name': 'Void Staff',
        'tier': 'Legendario',
        'slot_type': 'Daño',
        'gold_cost': 2800,
        'description': "Bastón del Vacío que penetra la resistencia mágica del objetivo, maximizando el daño de los magos contra tanques y objetivos resistentes.",
        'image_url': 'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/assets/items/icons2d/3135_mage_t3_voidstaff.png',
    },
    {
        'name': 'Frozen Heart',
        'tier': 'Legendario',
        'slot_type': 'Defensa',
        'gold_cost': 2500,
        'description': "Corazón helado que reduce la velocidad de ataque de los enemigos cercanos y otorga gran cantidad de armadura y reducción de enfriamiento.",
        'image_url': 'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/assets/items/icons2d/3110_tank_t3_frozenheart.png',
    },
    {
        'name': 'Spirit Visage',
        'tier': 'Legendario',
        'slot_type': 'Defensa',
        'gold_cost': 3000,
        'description': "Visaje espiritual que amplifica toda la curación recibida por el portador, combinado con resistencia mágica, vida y regeneración adicional.",
        'image_url': 'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/assets/items/icons2d/3065_tank_t3_spiritvisage.png',
    },
    {
        'name': "Dead Man's Plate",
        'tier': 'Legendario',
        'slot_type': 'Defensa',
        'gold_cost': 2900,
        'description': "Armadura fantasmal que acumula impulso al moverse, descargando ese momentum devastador en el siguiente ataque básico del portador.",
        'image_url': 'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/assets/items/icons2d/3742_tank_t3_deadmansplate.png',
    },
    {
        'name': 'Titanic Hydra',
        'tier': 'Legendario',
        'slot_type': 'Daño',
        'gold_cost': 3300,
        'description': "Hidra titánica que usa la vida máxima del portador para amplificar el daño de los ataques básicos en ráfagas de área devastadora.",
        'image_url': 'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/assets/items/icons2d/3748_fighter_t3_titanichydra.png',
    },
    {
        'name': "Nashor's Tooth",
        'tier': 'Legendario',
        'slot_type': 'Daño',
        'gold_cost': 3000,
        'description': "Diente de Nashor que potencia los ataques básicos de los magos añadiendo daño mágico proporcional al poder de habilidad del portador.",
        'image_url': 'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/assets/items/icons2d/3115_mage_t3_nashorstooth.png',
    },
    {
        'name': 'Lich Bane',
        'tier': 'Legendario',
        'slot_type': 'Daño',
        'gold_cost': 3000,
        'description': "Bastón que empodera al portador para devastar estructuras y enemigos con una ráfaga de daño mágico tras usar una habilidad en combate.",
        'image_url': 'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/assets/items/icons2d/3100_mage_t3_lichbane.png',
    },
    {
        'name': "Guinsoo's Rageblade",
        'tier': 'Legendario',
        'slot_type': 'Daño',
        'gold_cost': 3000,
        'description': "Hoja de furia que aumenta progresivamente la velocidad de ataque y convierte los críticos en efectos de ataque básico potenciado.",
        'image_url': 'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/assets/items/icons2d/3124_marksman_t3_guinsoosrageblade.png',
    },
    # ── Mítico ─────────────────────────────────────────────────────────────────
    {
        'name': 'Eclipse',
        'tier': 'Mítico',
        'slot_type': 'Daño',
        'gold_cost': 3500,
        'description': "Objeto mítico de asesino que otorga daño, penetración de armadura y un escudo periódico al golpear varios enemigos en rápida sucesión.",
        'image_url': 'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/assets/items/icons2d/6692_assassin_t4_eclipse.png',
    },
    {
        'name': 'Galeforce',
        'tier': 'Mítico',
        'slot_type': 'Daño',
        'gold_cost': 3400,
        'description': "Objeto mítico de tirador que proporciona un guión de reposicionamiento activo y una devastadora ráfaga de proyectiles al activarse en combate.",
        'image_url': 'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/assets/items/icons2d/6671_marksman_t4_galeforce.png',
    },
    {
        'name': 'Kraken Slayer',
        'tier': 'Mítico',
        'slot_type': 'Daño',
        'gold_cost': 3400,
        'description': "Objeto mítico que desgarra las defensas de los tanques enemigos con daño verdadero acumulado cada tres ataques básicos contra el mismo objetivo.",
        'image_url': 'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/assets/items/icons2d/6672_marksman_t4_behemothslayer.png',
    },
    {
        'name': 'Immortal Shieldbow',
        'tier': 'Mítico',
        'slot_type': 'Daño',
        'gold_cost': 3400,
        'description': "Objeto mítico que genera un escudo de vida cuando el portador cae por debajo del umbral crítico de salud, salvándole en el último momento.",
        'image_url': 'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/assets/items/icons2d/6673_marksman_t4_crimsonshieldbow.png',
    },
    {
        'name': 'Rod of Ages',
        'tier': 'Mítico',
        'slot_type': 'Utilidad',
        'gold_cost': 2800,
        'description': "Bastón que acumula cargas al subir de nivel, aumentando vida, maná y poder de habilidad progresivamente hasta alcanzar todo su potencial.",
        'image_url': 'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/assets/items/icons2d/6657_mage_t4_rodofages.png',
    },
    {
        'name': 'Heartsteel',
        'tier': 'Mítico',
        'slot_type': 'Defensa',
        'gold_cost': 3000,
        'description': "Objeto mítico que acumula vida permanente al golpear grandes campeones, convirtiéndose en una fuente inagotable de salud en partidas largas.",
        'image_url': 'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/assets/items/icons2d/3084_tank_t4_heartsteel.png',
    },
]


def _clean_name(name):
    """Convert item name to a safe filename (strip non-alphanumeric/space chars)."""
    return re.sub(r"[^a-zA-Z0-9 ]", '', name)


class Command(BaseCommand):
    help = 'Seed the database with items and download item icons from CommunityDragon.'

    def handle(self, *args, **options):
        self._seed_items()
        self._download_images()

    def _seed_items(self):
        for data in ITEMS:
            item, created = Item.objects.get_or_create(
                name=data['name'],
                defaults=data,
            )
            if created:
                self.stdout.write(f'  Item created: {item.name}')
            else:
                self.stdout.write(f'  Item already exists: {item.name}')

    def _download_images(self):
        try:
            import requests
        except ImportError:
            self.stdout.write(self.style.WARNING('requests not installed, skipping image download.'))
            return

        out_dir = os.path.join('static', 'wiki', 'items')
        os.makedirs(out_dir, exist_ok=True)

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        base = 'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default'

        self.stdout.write('Fetching item list from CommunityDragon...')
        try:
            r = requests.get(
                f'{base}/v1/items.json',
                headers=headers,
                timeout=30,
            )
            r.raise_for_status()
            all_items = r.json()
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Could not fetch item list: {e}'))
            return

        # Build case-insensitive name → iconPath lookup
        icon_map = {item['name'].lower(): item.get('iconPath', '') for item in all_items}

        for data in ITEMS:
            name = data['name']
            clean = _clean_name(name)
            dest = os.path.join(out_dir, f'{clean}.png')
            if os.path.exists(dest):
                self.stdout.write(f'  Already exists: {clean}.png')
                continue

            icon_path = icon_map.get(name.lower(), '')
            if not icon_path:
                # Fallback: use image_url from data directly
                url = data['image_url']
            else:
                url = base + '/' + icon_path.replace('/lol-game-data/assets/', '').lower()

            try:
                resp = requests.get(url, headers=headers, timeout=30)
                resp.raise_for_status()
                with open(dest, 'wb') as f:
                    f.write(resp.content)
                self.stdout.write(f'  Downloaded: {clean}.png ({len(resp.content)} bytes)')
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'  Failed {name}: {e}'))

        self.stdout.write(self.style.SUCCESS('Done.'))
