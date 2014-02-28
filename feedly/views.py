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
#!/usr/bin/python
# -*- coding: utf-8 -*-
from hub.control import Profiles,Passwords,Control,Places,Photos
from django.http import HttpResponse as response
from feed import Mosaic,Pages
from main import Efforia
from payments import PagSeguro,PayPal,Baskets
from models import Sellable

def profileview(request,name='me'):
    e = Efforia()
    if request.method == 'GET':
        return e.profile_view(request,name)

def basket(request):
    b = Baskets()
    if request.method == 'GET':
        return b.view_items(request)
    elif request.method == 'POST':
        return b.add_item(request)

def basketclean(request):
    b = Baskets()
    if request.method == 'GET':
        return b.clean_basket(request)

def pagseguro(request):
    p = PagSeguro()
    if request.method == 'GET':
        return p.process(request)

def pagsegurocart(request):
    p = PagSeguro()
    if request.method == 'GET':
        return p.process_cart(request)

def paypal(request):
    p = PayPal()
    if request.method == 'GET':
        return p.process(request)

def paypalcart(request):
    p = PayPal()
    if request.method == 'GET':
        return p.process_cart(request)

def pageview(request):
    p = Pages()
    if request.method == 'GET':
        return p.page_view(request)
    
def pageedit(request):
    p = Pages()
    if request.method == 'GET':
        return p.edit_page(request)
    elif request.method == 'POST':
        return p.save_page(request)

def page(request):
    p = Pages()
    if request.method == 'GET':
        return p.view_page(request)
    elif request.method == 'POST':
        return p.create_page(request)

def mosaic(request):
    m = Mosaic()
    if request.method == 'GET':
        return m.view_mosaic(request)

def deadlines(request):
    m = Mosaic()
    if request.method == 'GET':
        return m.deadlines(request)

def main(request):
    e = Efforia()
    if request.method == 'GET':
        return e.start(request)
    elif request.method == 'POST':
        return e.external(request)