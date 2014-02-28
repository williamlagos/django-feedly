from django.db.models import ForeignKey,TextField,CharField,IntegerField,DateTimeField,BooleanField,Model,FloatField
from django.contrib.auth.models import User
from feedly.models import Sellable
from datetime import date
import sys,os
path = os.path.abspath("efforia")
sys.path.append(path)

locale = ('Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez')

class Spreaded(Model):
    name = CharField(default='!!',max_length=10)
    user = ForeignKey(User,related_name='+')
    spread = IntegerField(default=1)
    spreaded = IntegerField(default=2)
    date = DateTimeField(auto_now_add=True)
    def token(self): return self.name[:2]
    def stoken(self): return self.name[:1]
    def month(self): return locale[self.date.month-1]

class Spreadable(Model):
    name = CharField(default='',max_length=50)
    user = ForeignKey(User,related_name='+')
    content = TextField()
    spreaded = CharField(default='efforia',max_length=15)
    date = DateTimeField(auto_now_add=True)
    def token(self): return self.name[:1]
    def name_trimmed(self): return self.name[1:]
    def month(self): return locale[self.date.month-1]
    
class Playable(Model):
    name = CharField(default='',max_length=150)
    user = ForeignKey(User,related_name='+')
    category = IntegerField(default=1)
    description = TextField()
    token = CharField(max_length=20)
    credit = IntegerField(default=0)
    visual = CharField(default='',max_length=40)
    date = DateTimeField(default=date.today(),auto_now_add=True)
    def etoken(self): return self.name[:1]
    def name_trimmed(self): return self.name[1:]
    def month(self): return locale[self.date.month-1]
    def date_formatted(self): return self.date.strftime('%Y-%m-%d %H:%M:%S.%f')
    
class Image(Model):
    name = CharField(default='!%',max_length=10)
    description = CharField(default='',max_length=140)
    link = CharField(default='',max_length=100)
    user = ForeignKey(User,related_name='+')
    date = DateTimeField(auto_now_add=True)
    def token(self): return self.name[:2]
    def name_trimmed(self): return self.name[2:]
    def month(self): return locale[self.date.month-1]
    def visual(self):
        client = httpclient.HTTPClient()
        response = client.fetch(self.visual)
        url = '%s?dl=1' % response.effective_url
        return url

class Product(Sellable):
    category = IntegerField(default=1)
    description = TextField()
    def token(self): return self.name[:3]
    def name_trimmed(self): return self.name.split(';')[0][2:]
    def month(self): return locale[self.date.month-1]
