from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import Group
from django.db.models import Avg, Count
from django.db.models import Q
from django.db.models.functions import Lower
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from rest_framework.generics import CreateAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.views import TokenObtainPairView

from wiki.forms import ChampionForm, ItemForm, RegionForm
from wiki.models import Champion, Item, Region
from wiki.permissions import HasRole
from wiki.serializers import (
    ChampionSerializer,
    CustomTokenSerializer,
    ItemSerializer,
    RegionSerializer,
    RegisterSerializer,
)


def home(request):
    return render(
        request,
        'wiki/home.html',
        {
            'champion_count': Champion.objects.count(),
            'region_count': Region.objects.count(),
            'item_count': Item.objects.count(),
            'latest_champions': Champion.objects.order_by('-release_year', Lower('name'))[:4],
            'latest_items': Item.objects.order_by(Lower('name'))[:4],
            'latest_regions': Region.objects.order_by(Lower('name'))[:4],
        },
    )


def register(request):
    form = UserCreationForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        fan_group, _ = Group.objects.get_or_create(name='Fan')
        user.groups.add(fan_group)
        return redirect('wiki:login')
    return render(
        request,
        'wiki/form.html',
        {'form': form, 'title': 'Crear cuenta', 'submit_label': 'Registrarme'},
    )


def stats(request):
    champions_by_role = list(
        Champion.objects.values('role').annotate(total=Count('id')).order_by('-total')
    )
    champions_by_region = list(
        Region.objects.annotate(total=Count('champions'))
        .values('name', 'total')
        .order_by('-total')
    )
    items_by_tier = list(
        Item.objects.values('tier').annotate(total=Count('id')).order_by('-total')
    )
    avg_item_cost_by_tier = list(
        Item.objects.values('tier').annotate(avg=Avg('gold_cost')).order_by('-avg')
    )
    champions_by_year = list(
        Champion.objects.values('release_year')
        .annotate(total=Count('id'))
        .order_by('release_year')
    )

    return render(
        request,
        'wiki/stats.html',
        {
            'total_champions': Champion.objects.count(),
            'total_regions': Region.objects.count(),
            'total_items': Item.objects.count(),
            'champions_by_role': champions_by_role,
            'champions_by_region': champions_by_region,
            'items_by_tier': items_by_tier,
            'avg_item_cost_by_tier': avg_item_cost_by_tier,
            'champions_by_year': champions_by_year,
            'role_labels': [item['role'] for item in champions_by_role],
            'role_values': [item['total'] for item in champions_by_role],
            'region_labels': [item['name'] for item in champions_by_region],
            'region_values': [item['total'] for item in champions_by_region],
            'tier_labels': [item['tier'] for item in items_by_tier],
            'tier_values': [item['total'] for item in items_by_tier],
            'avg_tier_labels': [item['tier'] for item in avg_item_cost_by_tier],
            'avg_tier_values': [
                round(float(item['avg'] or 0), 2) for item in avg_item_cost_by_tier
            ],
            'year_labels': [item['release_year'] for item in champions_by_year],
            'year_values': [item['total'] for item in champions_by_year],
        },
    )


class ChampionListView(ListView):
    model = Champion
    template_name = 'wiki/champion_list.html'
    context_object_name = 'champions'
    paginate_by = 6

    def get_queryset(self):
        queryset = super().get_queryset().prefetch_related('regions', 'featured_items')
        query = self.request.GET.get('q')
        if query:
            filters = (
                Q(name__icontains=query)
                | Q(title__icontains=query)
                | Q(role__icontains=query)
            )
            if query.isdigit():
                filters |= Q(release_year=int(query))
            queryset = queryset.filter(filters)

        sort = self.request.GET.get('sort', 'name')
        if sort == 'name':
            queryset = queryset.order_by(Lower('name'))
        elif sort == 'release_year':
            queryset = queryset.order_by('release_year')
        elif sort == 'role':
            queryset = queryset.order_by(Lower('role'))
        return queryset


class ChampionDetailView(DetailView):
    model = Champion
    template_name = 'wiki/champion_detail.html'
    context_object_name = 'champion'


class ChampionCreateView(PermissionRequiredMixin, CreateView):
    model = Champion
    form_class = ChampionForm
    template_name = 'wiki/form.html'
    success_url = reverse_lazy('wiki:champion_list')
    permission_required = 'wiki.add_champion'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Crear campeón'
        context['submit_label'] = 'Guardar campeón'
        return context


class ChampionUpdateView(PermissionRequiredMixin, UpdateView):
    model = Champion
    form_class = ChampionForm
    template_name = 'wiki/form.html'
    success_url = reverse_lazy('wiki:champion_list')
    permission_required = 'wiki.change_champion'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar campeón'
        context['submit_label'] = 'Actualizar campeón'
        return context


class ChampionDeleteView(PermissionRequiredMixin, DeleteView):
    model = Champion
    template_name = 'wiki/confirm_delete.html'
    success_url = reverse_lazy('wiki:champion_list')
    permission_required = 'wiki.delete_champion'
    context_object_name = 'object'


class RegionListView(ListView):
    model = Region
    template_name = 'wiki/region_list.html'
    context_object_name = 'regions'
    paginate_by = 6

    def get_queryset(self):
        return super().get_queryset().order_by(Lower('name'))


class RegionDetailView(DetailView):
    model = Region
    template_name = 'wiki/region_detail.html'
    context_object_name = 'region'


class RegionCreateView(PermissionRequiredMixin, CreateView):
    model = Region
    form_class = RegionForm
    template_name = 'wiki/form.html'
    success_url = reverse_lazy('wiki:region_list')
    permission_required = 'wiki.add_region'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Crear región'
        context['submit_label'] = 'Guardar región'
        return context


class RegionUpdateView(PermissionRequiredMixin, UpdateView):
    model = Region
    form_class = RegionForm
    template_name = 'wiki/form.html'
    success_url = reverse_lazy('wiki:region_list')
    permission_required = 'wiki.change_region'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar región'
        context['submit_label'] = 'Actualizar región'
        return context


class RegionDeleteView(PermissionRequiredMixin, DeleteView):
    model = Region
    template_name = 'wiki/confirm_delete.html'
    success_url = reverse_lazy('wiki:region_list')
    permission_required = 'wiki.delete_region'
    context_object_name = 'object'


class ItemListView(ListView):
    model = Item
    template_name = 'wiki/item_list.html'
    context_object_name = 'items'
    paginate_by = 6

    def get_queryset(self):
        return super().get_queryset().order_by(Lower('name'))


class ItemDetailView(DetailView):
    model = Item
    template_name = 'wiki/item_detail.html'
    context_object_name = 'item'


class ItemCreateView(PermissionRequiredMixin, CreateView):
    model = Item
    form_class = ItemForm
    template_name = 'wiki/form.html'
    success_url = reverse_lazy('wiki:item_list')
    permission_required = 'wiki.add_item'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Crear objeto'
        context['submit_label'] = 'Guardar objeto'
        return context


class ItemUpdateView(PermissionRequiredMixin, UpdateView):
    model = Item
    form_class = ItemForm
    template_name = 'wiki/form.html'
    success_url = reverse_lazy('wiki:item_list')
    permission_required = 'wiki.change_item'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar objeto'
        context['submit_label'] = 'Actualizar objeto'
        return context


class ItemDeleteView(PermissionRequiredMixin, DeleteView):
    model = Item
    template_name = 'wiki/confirm_delete.html'
    success_url = reverse_lazy('wiki:item_list')
    permission_required = 'wiki.delete_item'
    context_object_name = 'object'


class LorePagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 50


class ChampionViewSet(ModelViewSet):
    queryset = Champion.objects.all()
    serializer_class = ChampionSerializer
    pagination_class = LorePagination
    permission_classes = [IsAuthenticated, HasRole('Editor')]

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        if query:
            filters = (
                Q(name__icontains=query)
                | Q(title__icontains=query)
                | Q(role__icontains=query)
            )
            if query.isdigit():
                filters |= Q(release_year=int(query))
            queryset = queryset.filter(filters)

        sort = self.request.GET.get('sort', 'name')
        if sort == 'name':
            queryset = queryset.order_by(Lower('name'))
        elif sort == 'release_year':
            queryset = queryset.order_by('release_year')
        elif sort == 'role':
            queryset = queryset.order_by(Lower('role'))
        return queryset


class RegionViewSet(ModelViewSet):
    queryset = Region.objects.all().order_by(Lower('name'))
    serializer_class = RegionSerializer
    pagination_class = LorePagination
    permission_classes = [IsAuthenticated, HasRole('Editor')]


class ItemViewSet(ModelViewSet):
    queryset = Item.objects.all().order_by(Lower('name'))
    serializer_class = ItemSerializer
    pagination_class = LorePagination
    permission_classes = [IsAuthenticated, HasRole('Editor')]


class RegisterView(CreateAPIView):
    serializer_class = RegisterSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenSerializer
