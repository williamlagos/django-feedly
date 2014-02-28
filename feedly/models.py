#
# This file is part of Efforia project.
#
# Copyright (C) 2011-2013 William Oliveira de Lagos <william@efforia.com.br>
#
# Efforia is free software: you can redistribute it and/or modify
# it under the terms of the Lesser GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Efforia is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Efforia. If not, see <http://www.gnu.org/licenses/>.
#

from django.db.models import *
from django.conf import settings
from django.contrib.auth.models import User
from django.template import Context,Template
from datetime import date

locale = settings.LOCALE_DATE

def user(name): return User.objects.filter(username=name)[0]
def superuser(): return User.objects.filter(is_superuser=True)[0]

class Page(Model):
    name = CharField(default='!#',max_length=50)
    content = TextField(default='')
    user = ForeignKey(User,related_name='+')
    date = DateTimeField(auto_now_add=True)
    def token(self): return self.name[:2]
    def name_trimmed(self): return self.name[2:]
    def month(self): return locale[self.date.month-1]
    
class Basket(Model):
    name = CharField(default='++',max_length=2)
    user = ForeignKey(User,related_name='+')
    deliverable = BooleanField(default=False)
    product = IntegerField(default=1)
    date = DateTimeField(auto_now_add=True)
    def token(self): return self.name[:2]
    # def total_value(self): return self.quantity*self.product.credit
    # def product_trimmed(self): return self.product.name_trimmed()
    # def product_month(self): return self.product.real_month()

class Sellable(Model):
    name = CharField(default='$$',max_length=100)
    user = ForeignKey(User,related_name='+')
    paid = BooleanField(default=False)
    returnable = BooleanField(default=False)
    value = FloatField(default=1.00)
    visual = CharField(default='',max_length=150)
    sellid = IntegerField(default=1)
    date = DateTimeField(default=date.today(),auto_now_add=True)
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