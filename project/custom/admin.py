from django.contrib import admin

from custom.models import Department, User


class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'first_name', 'last_name']
    search_fields = ('email', 'first_name', 'last_name')

admin.site.register(Department)
admin.site.register(User, UserAdmin)
