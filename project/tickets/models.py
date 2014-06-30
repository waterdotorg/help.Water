import datetime
import os
import re

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db import models
from django.dispatch.dispatcher import receiver
from django.template.defaultfilters import slugify
from django.template.loader import render_to_string
from django.utils.timezone import utc

from custom.models import Department
from custom.utils import md5sum


class Ticket(models.Model):
    UNASSIGNED_STATUS = 'UA'
    ASSIGNED_STATUS = 'AS'
    IN_PROGRESS_STATUS = 'IP'
    DELETED_STATUS = 'DL'
    COMPLETED_STATUS = 'CP'

    STATUS_CODES = [
        (UNASSIGNED_STATUS, 'Unassigned'),
        (ASSIGNED_STATUS, 'Assigned'),
        (IN_PROGRESS_STATUS, 'In Progress'),
        (DELETED_STATUS, 'Deleted'),
        (COMPLETED_STATUS, 'Completed'),
    ]

    NOW_PRIORITY = 'NW'
    SOON_PRIORITY = 'SN'
    SOMEDAY_PRIORITY = 'SD'

    PRIORITY_CODES = [
        (NOW_PRIORITY, 'Now'),
        (SOON_PRIORITY, 'Soon'),
        (SOMEDAY_PRIORITY, 'Someday'),
    ]
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='author')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='user')
    department = models.ForeignKey(Department, blank=True, null=True)
    assigned = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True,
                                 null=True, related_name='assigned')
    title = models.CharField(max_length=1000)
    description = models.TextField()
    status = models.CharField(max_length=2, choices=STATUS_CODES,
                              default=UNASSIGNED_STATUS, db_index=True)
    priority = models.CharField(max_length=2, choices=PRIORITY_CODES,
                                default=SOON_PRIORITY, db_index=True)
    priortiy_admin = models.IntegerField(blank=True, null=True)
    watchers = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True,
                                      null=True, related_name='watchers')
    minutes_worked = models.IntegerField(blank=True, null=True)
    due_date = models.DateTimeField(blank=True, null=True)
    closed_date = models.DateTimeField(blank=True, null=True)
    resolution = models.TextField(blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'%s' % self.title

    def save(self, *args, **kwargs):
        new_ticket = False
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

            if self.assigned is None and old.assigned is not None:
                self.status = self.UNASSIGNED_STATUS
            elif self.assigned != old.assigned:
                self.status = self.ASSIGNED_STATUS

            if not old.resolution and self.resolution:
                if not self.closed_date:
                    self.closed_date = now
                self.status = self.COMPLETED_STATUS
        except Ticket.DoesNotExist:
            new_ticket = True
        super(Ticket, self).save(*args, **kwargs)

        if new_ticket:
            self.email_init()
            self.watch_init()
        else:
            if not old.resolution and self.resolution:
                self.email_resolved()

        if self.assigned:
            self.watch_assigned()

    def get_absolute_url(self):
        return reverse('tickets.views.ticket_detail', args=[str(self.pk)])

    def get_absolute_edit_url(self):
        return reverse('tickets.views.ticket_edit', args=[str(self.pk)])

    def get_status(self):
        return dict(self.STATUS_CODES).get(self.status)

    def get_priority(self):
        return dict(self.PRIORITY_CODES).get(self.priority)

    def email_init(self):
        ticket_emails = (TicketEmail.active_objects
                         .exclude(email=self.author.email)
                         .values_list('email', flat=True))
        if ticket_emails:
            dict_context = {
                'ticket': self,
            }
            message = render_to_string('tickets/email/init.txt', dict_context)
            send_mail(
                'New Ticket Received',
                message,
                settings.DEFAULT_FROM_EMAIL,
                list(ticket_emails)
            )

    def email_resolved(self):
        watcher_emails = self.watchers.all().values_list('email', flat=True)
        if watcher_emails:
            dict_context = {
                'ticket': self,
            }
            message = render_to_string('tickets/email/resolved.txt',
                                       dict_context)
            send_mail(
                'Ticket Resolved',
                message,
                settings.DEFAULT_FROM_EMAIL,
                list(watcher_emails),
            )

    def watch_init(self):
        if self.author.ticket_auto_watch:
            self.watchers.add(self.author)

    def watch_assigned(self):
        if self.assigned not in self.watchers.all():
            self.watchers.add(self.assigned)


class TicketComment(models.Model):
    ticket = models.ForeignKey(Ticket)
    author = models.ForeignKey(settings.AUTH_USER_MODEL)
    content = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'%s' % self.content[:50]

    def save(self, *args, **kwargs):
        new = False

        try:
            TicketComment.objects.get(pk=self.pk)
        except TicketComment.DoesNotExist:
            new = True

        super(TicketComment, self).save(*args, **kwargs)

        now = datetime.datetime.utcnow().replace(tzinfo=utc)
        self.ticket.updated_date = now
        self.ticket.save()

        if new:
            self.notify_watchers()

    def notify_watchers(self):
        watchers_qs = (self.ticket.watchers
                       .exclude(id=self.author.pk)
                       .values_list('email', flat=True))
        if watchers_qs:
            dict_context = {
                'ticket_comment': self,
            }
            message = render_to_string(
                'tickets/email/new-comment.txt',
                dict_context,
            )
            send_mail(
                'New Comment on %s' % self.ticket.title,
                message,
                settings.DEFAULT_FROM_EMAIL,
                list(watchers_qs),
            )


class TicketEmailManager(models.Manager):
    def get_queryset(self):
        now = datetime.datetime.utcnow().replace(tzinfo=utc)
        return super(TicketEmailManager, self).get_queryset().filter(
            models.Q(end_date__isnull=True) | models.Q(end_date__gte=now),
            start_date__lte=now,
            enabled=True,
        )


class TicketEmail(models.Model):
    email = models.EmailField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(blank=True, null=True)
    enabled = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    objects = models.Manager()
    active_objects = TicketEmailManager()

    def __unicode__(self):
        return u'%s' % self.email


def get_upload_to(instance, filename):
    """
    Get the path which should be appended to MEDIA_ROOT to
    determine the value of the url attribute.
    """
    prefix = getattr(settings, "FILE_STORAGE_PREFIX", "attachments")
    app_model = u"_".join((instance._meta.app_label,
                          instance._meta.object_name)).lower()
    return u"/".join(map(str, (prefix, app_model, filename)))


class TicketAttachment(models.Model):
    ticket = models.ForeignKey(Ticket)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    attachment = models.FileField(upload_to=get_upload_to, db_index=True)

    # Metadata about the file
    mimetype = models.CharField(max_length=1000, blank=True, null=True)
    slug = models.SlugField(max_length=1000, unique=True, blank=True,
                            editable=False)
    size = models.PositiveIntegerField(blank=True, editable=False)
    checksum = models.CharField(max_length=32, blank=True, editable=False)

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'%s' % self.filename

    @property
    def filename(self):
        return os.path.basename(self.attachment.name)

    @property
    def pre_slug(self):
        """
        Helper to create the string that gets slugified.
        """
        s = "-".join(map(str, (self._meta.object_name.lower(), self.pk,
                               os.path.basename(self.attachment.name))))
        return re.sub("[^\w+]", "-", s)

    @property
    def checksum_match(self):
        return md5sum(self.attachment.file) == self.checksum

    def clean(self):
        """
        This method is called before each save.
        """
        try:
            self.size = self.attachment.size
            if hasattr(self.attachment.file, "content_type"):
                self.mimetype = self.attachment.file.content_type
        except ValueError, e:
            raise ValidationError(e.args[0])

    def save(self, *args, **kwargs):
        if not self.pk:
            super(TicketAttachment, self).save(*args, **kwargs)
        self.slug = slugify(self.pre_slug)
        self.checksum = md5sum(self.attachment.file)
        super(TicketAttachment, self).save(force_update=True)


###########
# Signals #
###########

@receiver(models.signals.pre_save, sender=TicketAttachment)
def pre_save_callback(sender, instance, **kwargs):
    """
    Run clean before each save to set some values
    based on the uploaded attachment.
    """
    instance.clean()


@receiver(models.signals.post_save, sender=TicketAttachment)
def post_save_callback(sender, instance, created, **kwargs):
    """
    Sets a _created flag on the attachment instance to indicate
    that this is a new attachment.
    """
    if created:
        instance._created = True
