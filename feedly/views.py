#
# This file is part of Feedly Open Source Initiative.
#
# Copyright (C) 2011-2014 William Oliveira de Lagos <william@Feedly.com.br>
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

#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.http import HttpResponse as response
from django.views.decorators.cache import never_cache
from feed import Mosaic,Pages
from core import Feedly
from payments import PagSeguro,PayPal,Baskets,Cartridge
from models import Sellable
import logging, urlparse

logger = logging.getLogger("feedly.views")

@never_cache
def payment_redirect(request, order_id):
    p = Cartridge()
    return p.payment_redirect(request,order_id)

@never_cache
def payment_execute(request, template="shop/payment_confirmation.html"):
    p = Cartridge()
    return p.payment_execute(request,template)
    
def profileview(request,name='me'):
    e = Feedly()
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
    e = Feedly()
    if request.method == 'GET':
        return e.start(request)
    elif request.method == 'POST':
        return e.external(request)