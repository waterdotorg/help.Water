from django.db import models

from custom_user.models import AbstractEmailUser


class Department(models.Model):
    title = models.CharField(max_length=256)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'%s' % self.title


class User(AbstractEmailUser):
    """
    EmailUser with custom fields
    """
    first_name = models.CharField(max_length=128, blank=True)
    last_name = models.CharField(max_length=128, blank=True)
    department = models.ForeignKey(Department, blank=True, null=True)

    def __unicode__(self):
        return u'%s' % self.email

    def get_full_name(self):
        return u'%s %s' % (self.first_name, self.last_name)
