# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'GraphiteServiceCheck'
        db.create_table('main_graphiteservicecheck', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('service', self.gf('django.db.models.fields.related.ForeignKey')(related_name='graphiteservicecheck', to=orm['main.Service'])),
            ('silenced', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('alert_type', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('frequency', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('failures_before_alert', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('graphite_range', self.gf('django.db.models.fields.IntegerField')(default=300)),
            ('graphite_metric', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('graphite_lower_bound', self.gf('django.db.models.fields.FloatField')()),
            ('graphite_upper_bound', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal('main', ['GraphiteServiceCheck'])


    def backwards(self, orm):
        # Deleting model 'GraphiteServiceCheck'
        db.delete_table('main_graphiteservicecheck')


    models = {
        'main.codeservicecheck': {
            'Meta': {'object_name': 'CodeServiceCheck'},
            'alert_type': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'code_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'failures_before_alert': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'frequency': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'codeservicecheck'", 'to': "orm['main.Service']"}),
            'silenced': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'main.compareservicecheck': {
            'Meta': {'object_name': 'CompareServiceCheck'},
            'alert_type': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'comparator': ('django.db.models.fields.CharField', [], {'default': "'=='", 'max_length': '128'}),
            'compared_value': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'endpoint': ('django.db.models.fields.URLField', [], {'max_length': '256'}),
            'failures_before_alert': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'field': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'frequency': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'serialization': ('django.db.models.fields.CharField', [], {'default': "'json'", 'max_length': '128'}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'compareservicecheck'", 'to': "orm['main.Service']"}),
            'silenced': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'main.graphiteservicecheck': {
            'Meta': {'object_name': 'GraphiteServiceCheck'},
            'alert_type': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'failures_before_alert': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'frequency': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'graphite_lower_bound': ('django.db.models.fields.FloatField', [], {}),
            'graphite_metric': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'graphite_range': ('django.db.models.fields.IntegerField', [], {'default': '300'}),
            'graphite_upper_bound': ('django.db.models.fields.FloatField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'graphiteservicecheck'", 'to': "orm['main.Service']"}),
            'silenced': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'main.sensuservicecheck': {
            'Meta': {'object_name': 'SensuServiceCheck'},
            'alert_type': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'failures_before_alert': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'frequency': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'sensu_check_name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sensuservicecheck'", 'to': "orm['main.Service']"}),
            'silenced': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'main.service': {
            'Meta': {'object_name': 'Service'},
            'alert_type': ('django.db.models.fields.CharField', [], {'default': "'none'", 'max_length': '64'}),
            'email_contact': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'failures_before_alert': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'frequency': ('django.db.models.fields.CharField', [], {'default': "'*/5 * * * *'", 'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'pagerduty_key': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'silenced': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'umpire_range': ('django.db.models.fields.IntegerField', [], {'default': '300'})
        },
        'main.simpleservicecheck': {
            'Meta': {'object_name': 'SimpleServiceCheck'},
            'alert_type': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'endpoint': ('django.db.models.fields.URLField', [], {'max_length': '256'}),
            'failures_before_alert': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'frequency': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'simpleservicecheck'", 'to': "orm['main.Service']"}),
            'silenced': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'timeout': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'main.umpireservicecheck': {
            'Meta': {'object_name': 'UmpireServiceCheck'},
            'alert_type': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'failures_before_alert': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'frequency': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'umpireservicecheck'", 'to': "orm['main.Service']"}),
            'silenced': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'umpire_check_type': ('django.db.models.fields.CharField', [], {'default': "'static'", 'max_length': '64'}),
            'umpire_max': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'umpire_metric': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'umpire_min': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'umpire_percent_error': ('django.db.models.fields.FloatField', [], {'default': '0.25'}),
            'umpire_range': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'umpire_range_type': ('django.db.models.fields.CharField', [], {'default': "'current'", 'max_length': '64'})
        }
    }

    complete_apps = ['main']