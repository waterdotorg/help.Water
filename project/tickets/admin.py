from django.contrib import admin

from tickets.models import Ticket, TicketComment, TicketEmail, TicketAttachment


class TicketAdmin(admin.ModelAdmin):
    list_display = ['title', 'department', 'status', 'priority']


class TicketEmailAdmin(admin.ModelAdmin):
    list_display = ['email', 'start_date', 'end_date', 'enabled']

class TicketAttachmentAdmin(admin.ModelAdmin):
    list_display = ['attachment', 'ticket', 'created_date']

admin.site.register(Ticket, TicketAdmin)
admin.site.register(TicketEmail, TicketEmailAdmin)
admin.site.register(TicketAttachment, TicketAttachmentAdmin)
admin.site.register(TicketComment)
