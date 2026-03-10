from django.contrib.auth.views import LoginView, LogoutView
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from wiki import views

router = DefaultRouter(trailing_slash=False)
router.register('champions', views.ChampionViewSet, basename='api-champions')
router.register('regions', views.RegionViewSet, basename='api-regions')
router.register('items', views.ItemViewSet, basename='api-items')

urlpatterns = [
    path('', views.home, name='home'),
    path('register', views.register, name='register'),
    path(
        'login',
        LoginView.as_view(
            template_name='wiki/form.html',
            redirect_authenticated_user=True,
            extra_context={'title': 'Iniciar sesión', 'submit_label': 'Entrar'},
        ),
        name='login',
    ),
    path('logout', LogoutView.as_view(), name='logout'),
    path('stats', views.stats, name='stats'),
    path('champions', views.ChampionListView.as_view(), name='champion_list'),
    path('champions/create', views.ChampionCreateView.as_view(), name='champion_create'),
    path('champions/<int:pk>', views.ChampionDetailView.as_view(), name='champion_detail'),
    path('champions/<int:pk>/edit', views.ChampionUpdateView.as_view(), name='champion_edit'),
    path(
        'champions/<int:pk>/delete',
        views.ChampionDeleteView.as_view(),
        name='champion_delete',
    ),
    path('regions', views.RegionListView.as_view(), name='region_list'),
    path('regions/create', views.RegionCreateView.as_view(), name='region_create'),
    path('regions/<int:pk>', views.RegionDetailView.as_view(), name='region_detail'),
    path('regions/<int:pk>/edit', views.RegionUpdateView.as_view(), name='region_edit'),
    path('regions/<int:pk>/delete', views.RegionDeleteView.as_view(), name='region_delete'),
    path('items', views.ItemListView.as_view(), name='item_list'),
    path('items/create', views.ItemCreateView.as_view(), name='item_create'),
    path('items/<int:pk>', views.ItemDetailView.as_view(), name='item_detail'),
    path('items/<int:pk>/edit', views.ItemUpdateView.as_view(), name='item_edit'),
    path('items/<int:pk>/delete', views.ItemDeleteView.as_view(), name='item_delete'),
    path('api/login', views.CustomTokenObtainPairView.as_view(), name='api-login'),
    path('api/refresh', TokenRefreshView.as_view(), name='api-refresh'),
    path('api/register', views.RegisterView.as_view(), name='api-register'),
    path('api/', include(router.urls)),
]
