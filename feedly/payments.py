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

#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.shortcuts import render 
from django.http import HttpResponse as response
from django.conf import settings
from django.template import Context,Template
from django import forms
from models import Sellable,Basket,user
from forms import BasketForm
from feed import Mosaic

try:
    from django_pagseguro.pagseguro import CarrinhoPagSeguro,ItemPagSeguro
    from paypal.standard.forms import PayPalPaymentsForm
    from paypal.standard.widgets import ValueHiddenInput, ReservedValueHiddenInput
except ImportError,e:
    pass

class Baskets(Mosaic):
    def view_items(self,request):
        u = self.current_user(request); products = []
        basket = list(Basket.objects.filter(user=u))
        for b in basket: products.extend(Sellable.objects.filter(sellid=b.product))
        return self.view_mosaic(request,products)
    def add_item(self,request):
        u = self.current_user(request)
        prodid = int(request.REQUEST['id'])
        if 'value' in request.REQUEST:
            value = request.REQUEST['value']
            token = request.REQUEST['token']
            visual = request.REQUEST['visual']
            s = Sellable(user=u,name=token,value=value,sellid=prodid,visual=visual); s.save()
            if 'qty' in request.REQUEST:
                for i in range(int(request.REQUEST['qty'])-1):
                    s = Sellable(user=u,name=token,value=value,sellid=prodid,visual=visual); s.save()
        exists = Basket.objects.all().filter(user=u,product=prodid)
        if not len(exists): 
            basket = Basket(user=u,product=prodid)
            basket.save()
        return self.view_items(request)
    def process_cart(self,request):
        u = self.current_user(request); cart = []
        basket = list(Basket.objects.filter(user=u))
        for b in basket: 
            sellables = Sellable.objects.filter(sellid=b.product)
            for s in sellables:
                prod = {}
                prod['value'] = s.value
                prod['product'] = s.name
                prod['qty'] = '1'
                cart.append(prod)
        return self.process(request,cart)
    def clean_basket(self,request):
        u = self.current_user(request); cart = []
        basket = list(Basket.objects.filter(user=u))
        for b in basket: 
            Sellable.objects.filter(sellid=b.product).delete()
            b.delete()
        return response("Basket cleaned successfully")
    def process(self,request,cart=None):
        pass

class PagSeguro(Baskets):
    def process(self,request,cart=None):
        for k,v in request.REQUEST.iteritems():
            if 'product' in k: product = v
            elif 'value' in k: value = float(v)
            elif 'qty' in k: qty = int(v)
        try:
            carrinho = CarrinhoPagSeguro(ref_transacao=1); count = 0
            if cart is not None:
                for p in cart:
                    count += 1
                    carrinho.add_item(ItemPagSeguro(cod=count,descr=p['product'],quant=p['qty'],valor=p['value']))
            else:
                carrinho.add_item(ItemPagSeguro(cod=1,descr=product,quant=qty,valor=value))
        except (ImportError,NameError) as e:
            carrinho = BasketForm()
        t = Template("{{form}}")
        c = Context({'form':carrinho.form()})
        return response(t.render(c))

class PayPal(Baskets):
    def process(self,request,cart=None):
        for k,v in request.REQUEST.iteritems():
            if 'product' in k: product = v
            elif 'value' in k: value = float(v)
            elif 'qty' in k: qty = int(v)
        host = 'http://%s' % request.get_host()
        paypal = {
            'business':      settings.PAYPAL_RECEIVER_EMAIL,
            'notify_url':    '%s%s'%(host,settings.PAYPAL_NOTIFY_URL),
            'return_url':    '%s%s'%(host,settings.PAYPAL_RETURN_URL),
            'cancel_return': '%s%s'%(host,settings.PAYPAL_CANCEL_RETURN),
            'currency_code': 'BRL',
        }
        option = '_cart'; count = 0
        try:
            form_paypal = PayPalPaymentsForm(initial=paypal)
            if cart is not None:
                for p in cart:
                    count += 1
                    form_paypal.fields['amount_%i'%count] = forms.IntegerField(widget=ValueHiddenInput(),initial=p['value'])
                    form_paypal.fields['item_name_%i'%count] = forms.CharField(widget=ValueHiddenInput(),initial=p['product'])
                    form_paypal.fields['quantity_%i'%count] = forms.CharField(widget=ValueHiddenInput(),initial=p['qty'])
            else:
                form_paypal.fields['amount_1'] = forms.IntegerField(widget=ValueHiddenInput(),initial=value)
                form_paypal.fields['item_name_1'] = forms.CharField(widget=ValueHiddenInput(),initial=product)
                form_paypal.fields['quantity_1'] = forms.CharField(widget=ValueHiddenInput(),initial=str(qty))
            form_paypal.fields['cmd'] = forms.CharField(widget=ValueHiddenInput(),initial=option)        
            form_paypal.fields['upload'] = forms.CharField(widget=ValueHiddenInput(),initial='1')
        except (NameError,ImportError) as e:
            form_paypal = BasketForm(initial=paypal)
        t = Template('{{form}}')
        c = Context({'form':form_paypal.render()})
        return response(t.render(c))
