# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Niche.url'
        db.add_column(u'rotator_niche', 'url',
                      self.gf('django.db.models.fields.URLField')(default='http://cpagodfather.com/autoinsurance/pagea.php', max_length=200),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Niche.url'
        db.delete_column(u'rotator_niche', 'url')


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
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'rotator.account': {
            'AM': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'AM_IM_list': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'AM_email_list': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'AM_phone_list': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'Meta': {'ordering': "['username', 'capacity']", 'object_name': 'Account'},
            'capacity': ('django.db.models.fields.FloatField', [], {'default': '100'}),
            'company': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'accounts'", 'to': "orm['rotator.Company']"}),
            'daily_cap': ('django.db.models.fields.FloatField', [], {'default': '100'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_checked': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'last_payment_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'network': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'accounts'", 'to': "orm['rotator.Network']"}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'payment_frequency': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'payments_via': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'primary': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'recieved_check_once': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'stats_configured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '30'}),
            'today_revenue': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '5', 'decimal_places': '2', 'blank': 'True'}),
            'user_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'rotator.accountapi': {
            'Meta': {'object_name': 'AccountAPI'},
            'account': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'api'", 'unique': 'True', 'to': "orm['rotator.Account']"}),
            'affiliate_id': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'api_key': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'rotator.advertiser': {
            'Meta': {'ordering': "['name']", 'object_name': 'Advertiser'},
            'daily_cap': ('django.db.models.fields.FloatField', [], {'default': '25'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'rotator.advertiseraccountcapacity': {
            'Meta': {'object_name': 'AdvertiserAccountCapacity'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'advertiser_capacity'", 'to': "orm['rotator.Account']"}),
            'advertiser': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'account_capacity'", 'to': "orm['rotator.Advertiser']"}),
            'capacity': ('django.db.models.fields.FloatField', [], {'default': '25'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'rotator.capacity': {
            'Meta': {'object_name': 'Capacity'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'dailycap_capacity'", 'to': "orm['rotator.Account']"}),
            'advertiser': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'dailycap_capacity'", 'null': 'True', 'to': "orm['rotator.Advertiser']"}),
            'company': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'dailycap_capacity'", 'to': "orm['rotator.Company']"}),
            'date': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'offer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'dailycap_capacity'", 'to': "orm['rotator.Offer']"}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'dailycap_capacity'", 'to': "orm['rotator.Owner']"})
        },
        'rotator.company': {
            'Meta': {'object_name': 'Company'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'capacity': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'county': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'daily_cap': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'email_list': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'im_list': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name_list': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'companies'", 'to': "orm['rotator.Owner']"}),
            'phone_list': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '30'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'w9_file': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'websites': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'zip': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'})
        },
        'rotator.csvfile': {
            'Meta': {'object_name': 'CSVFile'},
            'cost': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'csv_files': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'csv_headers': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'date_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'filesize': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'has_header': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lead_source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rotator.LeadSource']"}),
            'max_offers': ('django.db.models.fields.FloatField', [], {'default': '1'}),
            'niche': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rotator.Niche']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '30'}),
            'uploaded_by': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'workers': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'assignments'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['auth.User']"})
        },
        'rotator.dailycap': {
            'Meta': {'object_name': 'DailyCap'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lead_list': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'offer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rotator.Offer']"}),
            'submits': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'worker_list': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'rotator.earnings': {
            'CTR': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'EPC': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '5', 'decimal_places': '2'}),
            'Meta': {'object_name': 'Earnings'},
            'aproved': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'aprovedCTR': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'campaign': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'clicks': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'eCPM': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '5', 'decimal_places': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'impressions': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'network': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rotator.Network']"}),
            'niche': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rotator.Niche']"}),
            'offer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rotator.Offer']"}),
            'payout': ('django.db.models.fields.DecimalField', [], {'max_digits': '5', 'decimal_places': '2'}),
            'qualified_transactions': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'revenue': ('django.db.models.fields.DecimalField', [], {'max_digits': '5', 'decimal_places': '2'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'})
        },
        'rotator.ipsolution': {
            'Meta': {'object_name': 'IPSolution'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'rotator.lead': {
            'Meta': {'object_name': 'Lead'},
            '_hard_lock': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "'hard_lock'"}),
            '_locked_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_column': "'locked_at'"}),
            '_locked_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'working_on_lead'", 'null': 'True', 'db_column': "'locked_by'", 'to': u"orm['auth.User']"}),
            'advertisers': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'leads'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['rotator.Advertiser']"}),
            'csv': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'leads'", 'to': "orm['rotator.CSVFile']"}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'ended_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'lead_data': ('django.db.models.fields.TextField', [], {}),
            'offers_completed': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'completed_leads'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['rotator.Offer']"}),
            'offers_requested': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'proposed_leads'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['rotator.Offer']"}),
            'started_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'subid': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'user_agent': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'worker': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'leads_in_work'", 'null': 'True', 'to': u"orm['auth.User']"})
        },
        'rotator.leadsource': {
            'Meta': {'object_name': 'LeadSource'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '30'})
        },
        'rotator.leadsourceofferexclusion': {
            'Meta': {'object_name': 'LeadSourceOfferExclusion'},
            'advertiser': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rotator.Advertiser']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'leadsource': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rotator.LeadSource']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '30'})
        },
        'rotator.manualqueue': {
            'Meta': {'object_name': 'ManualQueue'},
            'createdDate': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'size': ('django.db.models.fields.SmallIntegerField', [], {'default': '10'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '2000'})
        },
        'rotator.network': {
            'Meta': {'ordering': "['name']", 'object_name': 'Network'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'single': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '30'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'rotator.niche': {
            'Meta': {'ordering': "['name']", 'object_name': 'Niche'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_clicks': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'min_clicks': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '10'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '30'}),
            'url': ('django.db.models.fields.URLField', [], {'default': "'http://cpagodfather.com/autoinsurance/pagea.php'", 'max_length': '200'})
        },
        'rotator.offer': {
            'Meta': {'unique_together': "(('offer_num', 'account'),)", 'object_name': 'Offer'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'offers'", 'to': "orm['rotator.Account']"}),
            'advertiser': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'offers'", 'null': 'True', 'to': "orm['rotator.Advertiser']"}),
            'capacity': ('django.db.models.fields.FloatField', [], {'default': '10'}),
            'daily_cap': ('django.db.models.fields.FloatField', [], {'default': '10'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_clicks': ('django.db.models.fields.FloatField', [], {'default': '15.0', 'null': 'True', 'blank': 'True'}),
            'min_clicks': ('django.db.models.fields.FloatField', [], {'default': '5.0', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'network': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'offers'", 'to': "orm['rotator.Network']"}),
            'niche': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'offers'", 'to': "orm['rotator.Niche']"}),
            'offer_num': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'payout': ('django.db.models.fields.FloatField', [], {}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '30'}),
            'submits_today': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'submits_total': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '2000'})
        },
        'rotator.offerclicks': {
            'Meta': {'object_name': 'OfferClicks'},
            'clicks_remaining': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_click_date_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'offer_id': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rotator.Offer']"}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'rotator.offerqueue': {
            'Meta': {'object_name': 'OfferQueue'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'offer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'queues'", 'to': "orm['rotator.Offer']"}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'queues'", 'to': "orm['rotator.TrafficHolderOrder']"}),
            'size': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'})
        },
        'rotator.owner': {
            'Meta': {'object_name': 'Owner'},
            'capacity': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'daily_cap': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '30'})
        },
        'rotator.proxyserver': {
            'Meta': {'object_name': 'ProxyServer'},
            'exceptions': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'host': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'rotator.trafficholderorder': {
            'Meta': {'object_name': 'TrafficHolderOrder'},
            'approval_url': ('django.db.models.fields.CharField', [], {'max_length': '2000', 'null': 'True', 'blank': 'True'}),
            'clicks_received': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'clicks_total': ('django.db.models.fields.IntegerField', [], {'default': '1000000'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'hourly_rate': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order_id': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'orders'", 'to': "orm['rotator.Owner']"}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '36', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'awaiting approval'", 'max_length': '30'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'rotator.unknownoffer': {
            'Meta': {'object_name': 'UnknownOffer'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rotator.Account']"}),
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'network': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rotator.Network']"}),
            'offer_num': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'})
        },
        'rotator.workerprofile': {
            'Meta': {'object_name': 'WorkerProfile'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_solution': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rotator.IPSolution']", 'null': 'True', 'blank': 'True'}),
            'now_online': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'odesk_id': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '30'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        },
        'rotator.workmanager': {
            'Meta': {'object_name': 'WorkManager'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'workers_online': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['rotator']