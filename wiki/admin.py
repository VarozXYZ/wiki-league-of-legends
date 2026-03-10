from django.contrib import admin

from wiki.models import Champion, Item, Region

admin.site.register(Region)
admin.site.register(Item)
admin.site.register(Champion)
