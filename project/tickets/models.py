import datetime

from django.conf import settings
from django.db import models
from django.utils.timezone import utc

from custom.models import Department


class Ticket(models.Model):
    UNASSIGNED_STATUS = 'UA'
    ASSIGNED_STATUS = 'AS'
    IN_PROGRESS_STATUS = 'IP'
    DELETED_STATUS = 'DL'
    COMPLETED_STATUS = 'CP'

    STATUS_CODES = (
        UNASSIGNED_STATUS, 'Unassigned',
        ASSIGNED_STATUS, 'Assigned',
        IN_PROGRESS_STATUS, 'In Progress',
        DELETED_STATUS, 'Deleted',
        COMPLETED_STATUS, 'Completed',
    )

    NOW_PRIORITY = 'NW'
    SOON_PRIORITY = 'SN'
    SOMEDAY_PRIORITY = 'SD'

    PRIORITY_CODES = (
        NOW_PRIORITY, 'Now',
        SOON_PRIORITY, 'Soon',
        SOMEDAY_PRIORITY, 'Someday',
    )
    author = models.ForeignKey(settings.AUTH_USER_MODEL)
    department = models.ForeignKey(Department, blank=True, null=True)
    assigned = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True,
                                 null=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    status = models.CharField(max_length=2, choices=STATUS_CODES,
                              default=UNASSIGNED_STATUS, db_index=True)
    priority = models.CharField(max_length=2, choices=PRIORITY_CODES,
                                default=SOON_PRIORITY, db_index=True)
    priortiy_admin = models.IntegerField(blank=True, null=True)
    watchers = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True,
                                      null=True)
    minutes_worked = models.IntegerField(blank=True, null=True)
    due_date = models.DateTimeField(blank=True, null=True)
    closed_date = models.DateTimeField(blank=True, null=True)
    resolution = models.TextField(blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'%s' % self.title

    def save(self, *args, **kwargs):
        now = datetime.datetime.utcnow().replace(tzinfo=utc)
        try:
            old = Ticket.objects.get(pk=self.pk)
            if (self.status == self.DELETED_STATUS
                    and old.status != self.DELETED_STATUS):
                self.closed_date = now
                self.assigned = None
            elif (self.status == self.COMPLETED_STATUS
                    and old.status != self.COMPLETED_STATUS):
                self.closed_date = now
            elif self.assigned is None and old.assigned is not None:
                self.status = self.UNASSIGNED_STATUS
            elif self.assigned != old.assigned:
                self.status = self.ASSIGNED_STATUS
        except Ticket.DoesNotExist:
            pass
        super(Ticket, self).save(*args, **kwargs)


class TicketComment(models.Model):
    ticket = models.ForeginKey(Ticket)
    author = models.ForeignKey(settings.AUTH_USER_MODEL)
    content = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'%s' % self.title[:50]