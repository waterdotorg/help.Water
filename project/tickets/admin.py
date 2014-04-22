from django.contrib import admin

from tickets.models import Ticket, TicketComment


class TicketAdmin(admin.ModelAdmin):
    list_display = ['title', 'department', 'status', 'priority']

admin.site.register(Ticket, TicketAdmin)
admin.site.register(TicketComment)
