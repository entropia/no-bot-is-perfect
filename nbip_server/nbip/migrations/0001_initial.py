# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Bot'
        db.create_table(u'nbip_bot', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='bots', to=orm['auth.User'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal(u'nbip', ['Bot'])

        # Adding model 'Word'
        db.create_table(u'nbip_word', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('lemma', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('correct_explanation', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('reference', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(related_name='submitted_words', to=orm['auth.User'])),
            ('n_human_explanations', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('n_bot_explanations', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
        ))
        db.send_create_signal(u'nbip', ['Word'])

        # Adding model 'Explanation'
        db.create_table(u'nbip_explanation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('word', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nbip.Word'])),
            ('explanation', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='submitted_explanations', null=True, to=orm['auth.User'])),
            ('bot', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nbip.Bot'], null=True, blank=True)),
        ))
        db.send_create_signal(u'nbip', ['Explanation'])

        # Adding model 'GameRound'
        db.create_table(u'nbip_gameround', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('word', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nbip.Word'])),
            ('pos', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('guess', self.gf('nbip.models.GuessField')(null=True)),
            ('player', self.gf('django.db.models.fields.related.ForeignKey')(related_name='gamerounds', to=orm['auth.User'])),
        ))
        db.send_create_signal(u'nbip', ['GameRound'])

        # Adding model 'GameRoundEntry'
        db.create_table(u'nbip_gameroundentry', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('gameround', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nbip.GameRound'])),
            ('explanation', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nbip.Explanation'])),
            ('pos', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('guess', self.gf('nbip.models.GuessField')(null=True)),
        ))
        db.send_create_signal(u'nbip', ['GameRoundEntry'])

        # Adding unique constraint on 'GameRoundEntry', fields ['gameround', 'explanation', 'pos']
        db.create_unique(u'nbip_gameroundentry', ['gameround_id', 'explanation_id', 'pos'])


    def backwards(self, orm):
        # Removing unique constraint on 'GameRoundEntry', fields ['gameround', 'explanation', 'pos']
        db.delete_unique(u'nbip_gameroundentry', ['gameround_id', 'explanation_id', 'pos'])

        # Deleting model 'Bot'
        db.delete_table(u'nbip_bot')

        # Deleting model 'Word'
        db.delete_table(u'nbip_word')

        # Deleting model 'Explanation'
        db.delete_table(u'nbip_explanation')

        # Deleting model 'GameRound'
        db.delete_table(u'nbip_gameround')

        # Deleting model 'GameRoundEntry'
        db.delete_table(u'nbip_gameroundentry')


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
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'nbip.bot': {
            'Meta': {'object_name': 'Bot'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'bots'", 'to': u"orm['auth.User']"})
        },
        u'nbip.explanation': {
            'Meta': {'object_name': 'Explanation'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'submitted_explanations'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'bot': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['nbip.Bot']", 'null': 'True', 'blank': 'True'}),
            'explanation': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'word': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['nbip.Word']"})
        },
        u'nbip.gameround': {
            'Meta': {'object_name': 'GameRound'},
            'explanations': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'explanation+'", 'symmetrical': 'False', 'through': u"orm['nbip.GameRoundEntry']", 'to': u"orm['nbip.Explanation']"}),
            'guess': ('nbip.models.GuessField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'gamerounds'", 'to': u"orm['auth.User']"}),
            'pos': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'word': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['nbip.Word']"})
        },
        u'nbip.gameroundentry': {
            'Meta': {'ordering': "['pos']", 'unique_together': "(('gameround', 'explanation', 'pos'),)", 'object_name': 'GameRoundEntry'},
            'explanation': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['nbip.Explanation']"}),
            'gameround': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['nbip.GameRound']"}),
            'guess': ('nbip.models.GuessField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pos': ('django.db.models.fields.PositiveSmallIntegerField', [], {})
        },
        u'nbip.word': {
            'Meta': {'object_name': 'Word'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'submitted_words'", 'to': u"orm['auth.User']"}),
            'correct_explanation': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lemma': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'n_bot_explanations': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'n_human_explanations': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'reference': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        }
    }

    complete_apps = ['nbip']