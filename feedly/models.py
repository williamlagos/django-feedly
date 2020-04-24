#
# This file is part of Efforia Open Source Initiative.
#
# Copyright (C) 2011-2014 William Oliveira de Lagos <william@efforia.com.br>
#
# Feedly is free software: you can redistribute it and/or modify
# it under the terms of the Lesser GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Feedly is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Feedly. If not, see <http://www.gnu.org/licenses/>.
#

from django.db.models import *
from django.conf import settings
from django.contrib.auth.models import User
from django.template import Context,Template
from django.utils.timezone import now
from datetime import date

locale = settings.LOCALE_DATE

def user(name): return User.objects.filter(username=name)[0]
def superuser(): return User.objects.filter(is_superuser=True)[0]

class Profile(Model):
    user = ForeignKey(User,related_name='+', on_delete=CASCADE)
    coins = IntegerField(default=0)
    visual = CharField(default="",max_length=100)
    career = CharField(default='',max_length=50)
    birthday = DateTimeField(default=now)
    google_token = TextField(default="",max_length=120)
    twitter_token = TextField(default="",max_length=120)
    facebook_token = TextField(default="",max_length=120)
    bio = TextField(default='',max_length=140)
    date = DateTimeField(auto_now_add=True)
    def years_old(self): return datetime.timedelta(self.birthday,date.today)
    def token(self): return ''
    def get_username(self): return self.user.username
    def month(self): return locale[self.date.month-1]
    def render(self):
        source = """
            <div class="col-xs-12 col-sm-6 col-md-3 col-lg-2 brick">
                <a class="block profile" href="#" style="display:block; background:black">
                <div class="box profile">
                <div class="content">
                <h2 class="name">{{ firstname }}</h2>
                <div class="centered">{{ career }}</div>
                </div>
                {% if visual %}
                    <img src="{{ visual }}" width="100%"/>
                {% else %}
                    <h1 class="centered"><span class="glyphicon glyphicon-user big-glyphicon"></span></h1>
                {% endif %}
                <div class="content centered">
                {{ bio }}
                <div class="id hidden">{{ id }}</div></div></div>
                <div class="date"> Entrou em {{ day }} de {{month}}</div>
            </a></div>
        """
        return Template(source).render(Context({
            'firstname': self.user.first_name,
            'career':    self.career,
            'id':        self.id,
            'visual':    self.visual,
            'bio':       self.bio,
            'day':       self.date.day,
            'month':     self.month
        }))

class Page(Model):
    name = CharField(default='!#',max_length=50)
    content = TextField(default='')
    user = ForeignKey(User,related_name='+', on_delete=CASCADE)
    date = DateTimeField(auto_now_add=True)
    def token(self): return self.name[:2]
    def name_trimmed(self): return self.name[2:]
    def month(self): return locale[self.date.month-1]

class Basket(Model):
    name = CharField(default='++',max_length=2)
    user = ForeignKey(User,related_name='+', on_delete=CASCADE)
    deliverable = BooleanField(default=False)
    product = IntegerField(default=1)
    date = DateTimeField(auto_now_add=True)
    def token(self): return self.name[:2]
    # def total_value(self): return self.quantity*self.product.credit
    # def product_trimmed(self): return self.product.name_trimmed()
    # def product_month(self): return self.product.real_month()

class Sellable(Model):
    name = CharField(default='$$',max_length=100)
    user = ForeignKey(User,related_name='+', on_delete=CASCADE)
    paid = BooleanField(default=False)
    returnable = BooleanField(default=False)
    value = FloatField(default=1.00)
    visual = CharField(default='',max_length=150)
    sellid = IntegerField(default=1)
    date = DateTimeField(auto_now_add=True)
    def token(self): return '$$'
    def name_trimmed(self): return self.name
    def type_object(self): return self.name[:2]
    def render(self):
        source = """
            <div class="col-xs-12 col-sm-6 col-md-3 col-lg-2 brick">
                <a class="block sellable" href="#" style="display:block; background-color:white">
                <div class="box" style="background-color:#333">
                <div class="content">
                <h2 class="title" style="color:white">{{nametrim}}</h2>
                {% if paid %}
                    <h2 class="lightgreen"> Valor j&aacute; pago </h2>
                {% endif %}
                <h1 class="centered"><span class="label label-info big-label"> R$ {{value}}0 </span></h1>
                <h1 class="centered"><span class="glyphicon glyphicon-shopping-cart giant-glyphicon style="color:white; margin-bottom:10px"></span></h1>
                <div class="id hidden">{{id}}</div>
            </div></div></div></a></div>
        """
        return Template(source).render(Context({
            'nametrim':  object.name_trimmed,
            'paid':      object.paid,
            'id':        object.id,
            'value':     object.value,
            'bio':       object.bio,
            'day':       object.date.day,
            'month':     object.month
        }))

class Followed(Model):
    followed = IntegerField(default=1)
    follower = IntegerField(default=2)
    date = DateTimeField(auto_now_add=True)

Profile.year = property(lambda p: p.years_old())
Profile.name = property(lambda p: p.get_username())
User.profile = property(lambda u: Profile.objects.get_or_create(user=u)[0])
