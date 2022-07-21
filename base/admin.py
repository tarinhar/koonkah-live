from django.contrib import admin
from .models import Category, Station, Item, Reuse, User, Credit

# Register your models here.
admin.site.register(User)
admin.site.register(Category)
admin.site.register(Station)
admin.site.register(Item)
admin.site.register(Reuse)
admin.site.register(Credit)

