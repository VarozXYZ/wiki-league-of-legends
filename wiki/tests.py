from datetime import date

from django.contrib.auth.models import Group, Permission, User
from django.core.exceptions import ValidationError
from django.test import Client, TestCase
from django.urls import reverse

from wiki.forms import ChampionForm, ItemForm, RegionForm
from wiki.models import Champion, Item, Region


class BaseWikiTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.editor_group = Group.objects.create(name='Editor')
        permissions = Permission.objects.filter(
            content_type__app_label='wiki',
            codename__in=[
                'add_champion',
                'change_champion',
                'delete_champion',
                'view_champion',
                'add_region',
                'change_region',
                'delete_region',
                'view_region',
                'add_item',
                'change_item',
                'delete_item',
                'view_item',
            ],
        )
        self.editor_group.permissions.add(*permissions)
        self.editor = User.objects.create_user(username='editor', password='pass12345')
        self.editor.groups.add(self.editor_group)

        self.region = Region.objects.create(
            name='Demacia',
            short_code='DEM',
            capital='Gran ciudad de Demacia',
            faction='Reino',
            description='Demacia es un reino orgulloso, disciplinado y conocido por su orden militar y su tradición.',
            image_url='https://example.com/demacia.jpg',
        )
        self.item = Item.objects.create(
            name='Filo Infinito',
            tier='Legendario',
            slot_type='Daño',
            gold_cost=3400,
            description='Objeto de daño crítico muy popular entre tiradores que buscan rematar peleas largas.',
            image_url='https://example.com/ie.jpg',
        )
        self.champion = Champion.objects.create(
            name='Lux',
            title='La Dama Luminosa',
            role='Mago',
            resource_type='Mana',
            release_year=2010,
            lore='Lux es una maga de Demacia que lucha entre las exigencias de su reino y el peso de su propio poder mágico.',
            image_url='https://example.com/lux.jpg',
        )
        self.champion.regions.add(self.region)
        self.champion.featured_items.add(self.item)

    def login_editor(self):
        self.client.login(username='editor', password='pass12345')

    def assert_login_required(self, url):
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('wiki:login'), response.url)


class RegionModelTest(TestCase):
    def test_create_region(self):
        region = Region.objects.create(
            name='Noxus',
            short_code='NOX',
            capital='Bastión Inmortal',
            faction='Imperio',
            description='Noxus es un imperio expansionista cuya fuerza militar y ambición marcan cada rincón de Runaterra.',
            image_url='https://example.com/noxus.jpg',
        )
        self.assertEqual(str(region), 'Noxus')

    def test_region_name_min_length(self):
        region = Region(
            name='Io',
            short_code='ION',
            capital='Placidium',
            faction='Territorio mágico',
            description='Ionia tiene una historia extensa y una fuerte identidad espiritual en todo su territorio.',
            image_url='https://example.com/ionia.jpg',
        )
        with self.assertRaises(ValidationError):
            region.full_clean()

    def test_region_short_code_must_be_uppercase(self):
        region = Region(
            name='Ionia',
            short_code='ion',
            capital='Placidium',
            faction='Territorio mágico',
            description='Ionia tiene una historia extensa y una fuerte identidad espiritual en todo su territorio.',
            image_url='https://example.com/ionia.jpg',
        )
        with self.assertRaises(ValidationError):
            region.full_clean()

    def test_region_description_min_length(self):
        region = Region(
            name='Piltover',
            short_code='PIL',
            capital='Piltover',
            faction='Ciudad estado',
            description='Muy corta.',
            image_url='https://example.com/piltover.jpg',
        )
        with self.assertRaises(ValidationError):
            region.full_clean()

    def test_region_image_requires_https(self):
        region = Region(
            name='Shurima',
            short_code='SHU',
            capital='Shurima',
            faction='Imperio',
            description='Shurima es un desierto inmenso marcado por ruinas antiguas, ascensión y guerras legendarias.',
            image_url='http://example.com/shurima.jpg',
        )
        with self.assertRaises(ValidationError):
            region.full_clean()


class ItemModelTest(TestCase):
    def test_create_item(self):
        item = Item.objects.create(
            name='Bastón del Vacío',
            tier='Legendario',
            slot_type='Daño',
            gold_cost=3000,
            description='Objeto de penetración mágica pensado para magos que quieren romper defensas elevadas.',
            image_url='https://example.com/void.jpg',
        )
        self.assertEqual(str(item), 'Bastón del Vacío')

    def test_item_name_min_length(self):
        item = Item(
            name='Ar',
            tier='Inicial',
            slot_type='Utilidad',
            gold_cost=350,
            description='Objeto sencillo para iniciar la partida con utilidad básica y estadísticas discretas.',
            image_url='https://example.com/start.jpg',
        )
        with self.assertRaises(ValidationError):
            item.full_clean()

    def test_item_min_gold_cost(self):
        item = Item(
            name='Espada barata',
            tier='Inicial',
            slot_type='Daño',
            gold_cost=200,
            description='Objeto de prueba para comprobar la validación del coste mínimo dentro del proyecto.',
            image_url='https://example.com/cheap.jpg',
        )
        with self.assertRaises(ValidationError):
            item.full_clean()

    def test_item_requires_https_image(self):
        item = Item(
            name='Égida solar',
            tier='Legendario',
            slot_type='Defensa',
            gold_cost=2700,
            description='Objeto defensivo con daño de área pensado para campeones frontales y peleas extensas.',
            image_url='http://example.com/aegis.jpg',
        )
        with self.assertRaises(ValidationError):
            item.full_clean()

    def test_mythic_item_requires_high_cost(self):
        item = Item(
            name='Mítico barato',
            tier='Mítico',
            slot_type='Daño',
            gold_cost=2000,
            description='Objeto de prueba para forzar la validación de coste mínimo para tiers míticos.',
            image_url='https://example.com/mythic.jpg',
        )
        with self.assertRaises(ValidationError):
            item.full_clean()


class ChampionModelTest(TestCase):
    def setUp(self):
        self.region = Region.objects.create(
            name='Ionia',
            short_code='ION',
            capital='Placidium',
            faction='Territorio mágico',
            description='Ionia agrupa tierras espirituales y tradiciones místicas repartidas entre múltiples provincias.',
            image_url='https://example.com/ionia.jpg',
        )

    def test_create_champion(self):
        champion = Champion.objects.create(
            name='Ahri',
            title='La Zorra de Nueve Colas',
            role='Mago',
            resource_type='Mana',
            release_year=2011,
            lore='Ahri es una vastaya que explora su identidad mientras domina la magia y sus recuerdos fragmentados del pasado.',
            image_url='https://example.com/ahri.jpg',
        )
        champion.regions.add(self.region)
        self.assertEqual(str(champion), 'Ahri - La Zorra de Nueve Colas')

    def test_champion_name_min_length(self):
        champion = Champion(
            name='A',
            title='Título válido',
            role='Mago',
            resource_type='Mana',
            release_year=2012,
            lore='Texto de lore suficientemente largo para validar el campeón sin fallar por longitud general.',
            image_url='https://example.com/a.jpg',
        )
        with self.assertRaises(ValidationError):
            champion.full_clean()

    def test_champion_release_year_not_future(self):
        champion = Champion(
            name='KaiSa',
            title='Hija del Vacío',
            role='Tirador',
            resource_type='Mana',
            release_year=date.today().year + 1,
            lore='KaiSa sobrevivió en el Vacío y regresó convertida en una cazadora marcada por la supervivencia.',
            image_url='https://example.com/kaisa.jpg',
        )
        with self.assertRaises(ValidationError):
            champion.full_clean()

    def test_champion_lore_min_length(self):
        champion = Champion(
            name='Sett',
            title='El jefe',
            role='Luchador',
            resource_type='Furia',
            release_year=2020,
            lore='Muy corto.',
            image_url='https://example.com/sett.jpg',
        )
        with self.assertRaises(ValidationError):
            champion.full_clean()

    def test_tirador_cannot_use_fury(self):
        champion = Champion(
            name='Prueba',
            title='Tirador experimental',
            role='Tirador',
            resource_type='Furia',
            release_year=2016,
            lore='Este campeón se usa únicamente para validar la regla cruzada entre rol y tipo de recurso.',
            image_url='https://example.com/test.jpg',
        )
        with self.assertRaises(ValidationError):
            champion.full_clean()


class RegionFormTest(TestCase):
    def test_region_form_is_valid(self):
        form = RegionForm(
            {
                'name': 'Freljord',
                'short_code': 'FRE',
                'capital': 'No única',
                'faction': 'Tribu',
                'description': 'Freljord es una tierra helada de clanes enfrentados, profecías antiguas y guerras por la supervivencia.',
                'image_url': 'https://example.com/freljord.jpg',
            }
        )
        self.assertTrue(form.is_valid())

    def test_region_form_name_required_message(self):
        form = RegionForm(
            {
                'name': '',
                'short_code': 'FRE',
                'capital': 'No única',
                'faction': 'Tribu',
                'description': 'Freljord es una tierra helada de clanes enfrentados, profecías antiguas y guerras por la supervivencia.',
                'image_url': 'https://example.com/freljord.jpg',
            }
        )
        self.assertEqual(form.errors['name'][0], 'Debes indicar el nombre de la región.')

    def test_region_form_short_code_min_length_message(self):
        form = RegionForm(
            {
                'name': 'Freljord',
                'short_code': 'F',
                'capital': 'No única',
                'faction': 'Tribu',
                'description': 'Freljord es una tierra helada de clanes enfrentados, profecías antiguas y guerras por la supervivencia.',
                'image_url': 'https://example.com/freljord.jpg',
            }
        )
        self.assertEqual(form.errors['short_code'][0], 'El código debe tener al menos 2 caracteres.')

    def test_region_form_uppercase_validator(self):
        form = RegionForm(
            {
                'name': 'Freljord',
                'short_code': 'fre',
                'capital': 'No única',
                'faction': 'Tribu',
                'description': 'Freljord es una tierra helada de clanes enfrentados, profecías antiguas y guerras por la supervivencia.',
                'image_url': 'https://example.com/freljord.jpg',
            }
        )
        self.assertEqual(form.errors['short_code'][0], 'El código debe estar en mayúsculas.')

    def test_region_form_https_validator(self):
        form = RegionForm(
            {
                'name': 'Freljord',
                'short_code': 'FRE',
                'capital': 'No única',
                'faction': 'Tribu',
                'description': 'Freljord es una tierra helada de clanes enfrentados, profecías antiguas y guerras por la supervivencia.',
                'image_url': 'http://example.com/freljord.jpg',
            }
        )
        self.assertEqual(form.errors['image_url'][0], 'La URL debe empezar por https://')


class ItemFormTest(TestCase):
    def test_item_form_is_valid(self):
        form = ItemForm(
            {
                'name': 'Huracán de Runaan',
                'tier': 'Legendario',
                'slot_type': 'Daño',
                'gold_cost': 2900,
                'description': 'Objeto orientado a tiradores que quieren aplicar efectos de impacto sobre varios objetivos.',
                'image_url': 'https://example.com/runaan.jpg',
            }
        )
        self.assertTrue(form.is_valid())

    def test_item_form_name_required_message(self):
        form = ItemForm(
            {
                'name': '',
                'tier': 'Legendario',
                'slot_type': 'Daño',
                'gold_cost': 2900,
                'description': 'Objeto orientado a tiradores que quieren aplicar efectos de impacto sobre varios objetivos.',
                'image_url': 'https://example.com/runaan.jpg',
            }
        )
        self.assertEqual(form.errors['name'][0], 'Debes indicar el nombre del objeto.')

    def test_item_form_min_value_message(self):
        form = ItemForm(
            {
                'name': 'Objeto barato',
                'tier': 'Inicial',
                'slot_type': 'Utilidad',
                'gold_cost': 200,
                'description': 'Objeto orientado a validar el mensaje personalizado de coste mínimo dentro del formulario.',
                'image_url': 'https://example.com/start.jpg',
            }
        )
        self.assertEqual(form.errors['gold_cost'][0], 'El coste mínimo permitido es 300.')

    def test_item_form_https_validator(self):
        form = ItemForm(
            {
                'name': 'Objeto mágico',
                'tier': 'Épico',
                'slot_type': 'Utilidad',
                'gold_cost': 900,
                'description': 'Objeto pensado para comprobar la validación de la URL de imagen en el formulario.',
                'image_url': 'http://example.com/item.jpg',
            }
        )
        self.assertEqual(form.errors['image_url'][0], 'La URL debe empezar por https://')

    def test_item_form_mythic_cost_rule(self):
        form = ItemForm(
            {
                'name': 'Mítico barato',
                'tier': 'Mítico',
                'slot_type': 'Daño',
                'gold_cost': 2000,
                'description': 'Objeto creado para lanzar la validación cruzada de coste mínimo según el tier mítico.',
                'image_url': 'https://example.com/mythic.jpg',
            }
        )
        self.assertEqual(
            form.errors['gold_cost'][0],
            'Un objeto mítico debe costar al menos 2600 de oro.',
        )


class ChampionFormTest(TestCase):
    def setUp(self):
        self.region = Region.objects.create(
            name='Zaun',
            short_code='ZAU',
            capital='Zaun',
            faction='Ciudad estado',
            description='Zaun es una ciudad subterránea marcada por la química extrema, el ingenio y la supervivencia.',
            image_url='https://example.com/zaun.jpg',
        )
        self.item = Item.objects.create(
            name='Diente de Nashor',
            tier='Legendario',
            slot_type='Daño',
            gold_cost=3000,
            description='Objeto híbrido muy usado por campeones que mezclan daño mágico con velocidad de ataque.',
            image_url='https://example.com/nashor.jpg',
        )

    def test_champion_form_is_valid(self):
        form = ChampionForm(
            {
                'name': 'Ekko',
                'title': 'El Chico que Rompió el Tiempo',
                'role': 'Asesino',
                'resource_type': 'Mana',
                'release_year': 2015,
                'lore': 'Ekko es un genio de Zaun que manipula el tiempo para rehacer errores y proteger a los suyos.',
                'image_url': 'https://example.com/ekko.jpg',
                'regions': [self.region.pk],
                'featured_items': [self.item.pk],
            }
        )
        self.assertTrue(form.is_valid())

    def test_champion_form_name_required_message(self):
        form = ChampionForm(
            {
                'name': '',
                'title': 'El Chico que Rompió el Tiempo',
                'role': 'Asesino',
                'resource_type': 'Mana',
                'release_year': 2015,
                'lore': 'Ekko es un genio de Zaun que manipula el tiempo para rehacer errores y proteger a los suyos.',
                'image_url': 'https://example.com/ekko.jpg',
                'regions': [self.region.pk],
            }
        )
        self.assertEqual(form.errors['name'][0], 'Debes indicar el nombre del campeón.')

    def test_champion_form_requires_region(self):
        form = ChampionForm(
            {
                'name': 'Ekko',
                'title': 'El Chico que Rompió el Tiempo',
                'role': 'Asesino',
                'resource_type': 'Mana',
                'release_year': 2015,
                'lore': 'Ekko es un genio de Zaun que manipula el tiempo para rehacer errores y proteger a los suyos.',
                'image_url': 'https://example.com/ekko.jpg',
            }
        )
        self.assertEqual(form.errors['regions'][0], 'Debes asignar al menos una región.')

    def test_champion_form_future_year(self):
        form = ChampionForm(
            {
                'name': 'Ekko',
                'title': 'El Chico que Rompió el Tiempo',
                'role': 'Asesino',
                'resource_type': 'Mana',
                'release_year': date.today().year + 1,
                'lore': 'Ekko es un genio de Zaun que manipula el tiempo para rehacer errores y proteger a los suyos.',
                'image_url': 'https://example.com/ekko.jpg',
                'regions': [self.region.pk],
            }
        )
        self.assertEqual(form.errors['release_year'][0], 'El año no puede estar en el futuro.')

    def test_champion_form_cross_validation(self):
        form = ChampionForm(
            {
                'name': 'Prueba',
                'title': 'Tirador experimental',
                'role': 'Tirador',
                'resource_type': 'Furia',
                'release_year': 2018,
                'lore': 'Campeón de prueba creado para lanzar la validación cruzada de recurso y rol dentro del formulario.',
                'image_url': 'https://example.com/test.jpg',
                'regions': [self.region.pk],
            }
        )
        self.assertEqual(
            form.errors['resource_type'][0],
            'Los tiradores de esta wiki no pueden usar furia.',
        )


class WikiViewTest(BaseWikiTestCase):
    def test_home_without_login(self):
        response = self.client.get(reverse('wiki:home'))
        self.assertEqual(response.status_code, 200)

    def test_home_with_login(self):
        self.login_editor()
        response = self.client.get(reverse('wiki:home'))
        self.assertEqual(response.status_code, 200)

    def test_stats_without_login(self):
        response = self.client.get(reverse('wiki:stats'))
        self.assertEqual(response.status_code, 200)

    def test_stats_with_login(self):
        self.login_editor()
        response = self.client.get(reverse('wiki:stats'))
        self.assertEqual(response.status_code, 200)

    def test_champion_list_without_login(self):
        response = self.client.get(reverse('wiki:champion_list'))
        self.assertEqual(response.status_code, 200)

    def test_champion_list_with_login(self):
        self.login_editor()
        response = self.client.get(reverse('wiki:champion_list'))
        self.assertEqual(response.status_code, 200)

    def test_champion_list_search_by_year(self):
        response = self.client.get(reverse('wiki:champion_list'), {'q': '2010'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Lux')
        self.assertNotContains(response, '2011')

    def test_champion_detail_without_login(self):
        response = self.client.get(reverse('wiki:champion_detail', kwargs={'pk': self.champion.pk}))
        self.assertEqual(response.status_code, 200)

    def test_champion_detail_with_login(self):
        self.login_editor()
        response = self.client.get(reverse('wiki:champion_detail', kwargs={'pk': self.champion.pk}))
        self.assertEqual(response.status_code, 200)

    def test_champion_create_without_login(self):
        self.assert_login_required(reverse('wiki:champion_create'))

    def test_champion_create_with_permission(self):
        self.login_editor()
        response = self.client.get(reverse('wiki:champion_create'))
        self.assertEqual(response.status_code, 200)

    def test_champion_edit_without_login(self):
        self.assert_login_required(reverse('wiki:champion_edit', kwargs={'pk': self.champion.pk}))

    def test_champion_edit_with_permission(self):
        self.login_editor()
        response = self.client.get(reverse('wiki:champion_edit', kwargs={'pk': self.champion.pk}))
        self.assertEqual(response.status_code, 200)

    def test_champion_delete_without_login(self):
        self.assert_login_required(reverse('wiki:champion_delete', kwargs={'pk': self.champion.pk}))

    def test_champion_delete_with_permission(self):
        self.login_editor()
        response = self.client.get(reverse('wiki:champion_delete', kwargs={'pk': self.champion.pk}))
        self.assertEqual(response.status_code, 200)

    def test_region_list_without_login(self):
        response = self.client.get(reverse('wiki:region_list'))
        self.assertEqual(response.status_code, 200)

    def test_region_list_with_login(self):
        self.login_editor()
        response = self.client.get(reverse('wiki:region_list'))
        self.assertEqual(response.status_code, 200)

    def test_region_detail_without_login(self):
        response = self.client.get(reverse('wiki:region_detail', kwargs={'pk': self.region.pk}))
        self.assertEqual(response.status_code, 200)

    def test_region_detail_with_login(self):
        self.login_editor()
        response = self.client.get(reverse('wiki:region_detail', kwargs={'pk': self.region.pk}))
        self.assertEqual(response.status_code, 200)

    def test_region_create_without_login(self):
        self.assert_login_required(reverse('wiki:region_create'))

    def test_region_create_with_permission(self):
        self.login_editor()
        response = self.client.get(reverse('wiki:region_create'))
        self.assertEqual(response.status_code, 200)

    def test_region_edit_without_login(self):
        self.assert_login_required(reverse('wiki:region_edit', kwargs={'pk': self.region.pk}))

    def test_region_edit_with_permission(self):
        self.login_editor()
        response = self.client.get(reverse('wiki:region_edit', kwargs={'pk': self.region.pk}))
        self.assertEqual(response.status_code, 200)

    def test_region_delete_without_login(self):
        self.assert_login_required(reverse('wiki:region_delete', kwargs={'pk': self.region.pk}))

    def test_region_delete_with_permission(self):
        self.login_editor()
        response = self.client.get(reverse('wiki:region_delete', kwargs={'pk': self.region.pk}))
        self.assertEqual(response.status_code, 200)

    def test_item_list_without_login(self):
        response = self.client.get(reverse('wiki:item_list'))
        self.assertEqual(response.status_code, 200)

    def test_item_list_with_login(self):
        self.login_editor()
        response = self.client.get(reverse('wiki:item_list'))
        self.assertEqual(response.status_code, 200)

    def test_item_detail_without_login(self):
        response = self.client.get(reverse('wiki:item_detail', kwargs={'pk': self.item.pk}))
        self.assertEqual(response.status_code, 200)

    def test_item_detail_with_login(self):
        self.login_editor()
        response = self.client.get(reverse('wiki:item_detail', kwargs={'pk': self.item.pk}))
        self.assertEqual(response.status_code, 200)

    def test_item_create_without_login(self):
        self.assert_login_required(reverse('wiki:item_create'))

    def test_item_create_with_permission(self):
        self.login_editor()
        response = self.client.get(reverse('wiki:item_create'))
        self.assertEqual(response.status_code, 200)

    def test_item_edit_without_login(self):
        self.assert_login_required(reverse('wiki:item_edit', kwargs={'pk': self.item.pk}))

    def test_item_edit_with_permission(self):
        self.login_editor()
        response = self.client.get(reverse('wiki:item_edit', kwargs={'pk': self.item.pk}))
        self.assertEqual(response.status_code, 200)

    def test_item_delete_without_login(self):
        self.assert_login_required(reverse('wiki:item_delete', kwargs={'pk': self.item.pk}))

    def test_item_delete_with_permission(self):
        self.login_editor()
        response = self.client.get(reverse('wiki:item_delete', kwargs={'pk': self.item.pk}))
        self.assertEqual(response.status_code, 200)
