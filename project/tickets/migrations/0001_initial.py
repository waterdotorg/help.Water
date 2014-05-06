# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Ticket'
        db.create_table(u'tickets_ticket', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(related_name='author', to=orm['custom.User'])),
            ('department', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['custom.Department'], null=True, blank=True)),
            ('assigned', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='assigned', null=True, to=orm['custom.User'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('status', self.gf('django.db.models.fields.CharField')(default='UA', max_length=2, db_index=True)),
            ('priority', self.gf('django.db.models.fields.CharField')(default='SN', max_length=2, db_index=True)),
            ('priortiy_admin', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('minutes_worked', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('due_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('closed_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('resolution', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('created_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'tickets', ['Ticket'])

        # Adding M2M table for field watchers on 'Ticket'
        m2m_table_name = db.shorten_name(u'tickets_ticket_watchers')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('ticket', models.ForeignKey(orm[u'tickets.ticket'], null=False)),
            ('user', models.ForeignKey(orm[u'custom.user'], null=False))
        ))
        db.create_unique(m2m_table_name, ['ticket_id', 'user_id'])

        # Adding model 'TicketComment'
        db.create_table(u'tickets_ticketcomment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ticket', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tickets.Ticket'])),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['custom.User'])),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('created_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'tickets', ['TicketComment'])


    def backwards(self, orm):
        # Deleting model 'Ticket'
        db.delete_table(u'tickets_ticket')

        # Removing M2M table for field watchers on 'Ticket'
        db.delete_table(db.shorten_name(u'tickets_ticket_watchers'))

        # Deleting model 'TicketComment'
        db.delete_table(u'tickets_ticketcomment')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'custom.department': {
            'Meta': {'object_name': 'Department'},
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'updated_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'custom.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'department': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['custom.Department']", 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"})
        },
        u'tickets.ticket': {
            'Meta': {'object_name': 'Ticket'},
            'assigned': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'assigned'", 'null': 'True', 'to': u"orm['custom.User']"}),
            'author': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'author'", 'to': u"orm['custom.User']"}),
            'closed_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'department': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['custom.Department']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'due_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'minutes_worked': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'priority': ('django.db.models.fields.CharField', [], {'default': "'SN'", 'max_length': '2', 'db_index': 'True'}),
            'priortiy_admin': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'resolution': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'UA'", 'max_length': '2', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'updated_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'watchers': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'watchers'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['custom.User']"})
        },
        u'tickets.ticketcomment': {
            'Meta': {'object_name': 'TicketComment'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['custom.User']"}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ticket': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tickets.Ticket']"}),
            'updated_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['tickets']