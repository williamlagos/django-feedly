#
# This file is part of Efforia Open Source Initiative.
#
# Copyright (C) 2011-2014 William Oliveira de Lagos <william@efforia.com.br>
#
# Shipping is free software: you can redistribute it and/or modify
# it under the terms of the Lesser GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Shipping is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Shipping. If not, see <http://www.gnu.org/licenses/>.
#
#!/usr/bin/python
# -*- coding: utf-8 -*-

import locale,paypalrestsdk,pagseguro,os
from django.utils.translation import ugettext as _
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse as response
from django.template import Template,Context
from django.http import HttpResponseRedirect as redirect

try:
	from shipping.codes import CorreiosCode
	from mezzanine.conf import settings
	from cartridge.shop.forms import OrderForm
	from cartridge.shop.models import Cart
	from cartridge.shop.checkout import CheckoutError
except ImportError,e:
	pass

def paypal_api():
	try:
		PAYPAL_CLIENT_ID = settings.PAYPAL_CLIENT_ID
		PAYPAL_CLIENT_SECRET = settings.PAYPAL_CLIENT_SECRET
	except AttributeError:
		raise ImproperlyConfigured(_("Credenciais de acesso ao paypal estao faltando, "
								 "isso inclui PAYPAL_CLIENT_ID e PAYPAL_SECRET "
								 "basta inclui-las no settings.py para serem utilizadas "
								 "no processador de pagamentos do paypal."))

	if settings.DEBUG: mode = 'sandbox'
	else: mode = 'live'

	api = paypalrestsdk.set_config(
		mode = mode, # sandbox or live
		client_id = PAYPAL_CLIENT_ID,
		client_secret = PAYPAL_CLIENT_SECRET
	)
	access_token = api.get_token()

	os.environ['PAYPAL_MODE'] = mode # sandbox or live
	os.environ['PAYPAL_CLIENT_ID'] = PAYPAL_CLIENT_ID
	os.environ['PAYPAL_CLIENT_SECRET'] = PAYPAL_CLIENT_SECRET

def pagseguro_api():
	api = pagseguro.PagSeguro(email=settings.PAGSEGURO_EMAIL_COBRANCA, 
				  			 token=settings.PAGSEGURO_TOKEN)
	return api

def paypal_payment(request,items,price,currency):
	paypal_api()
	server_host = request.get_host()
	payment = paypalrestsdk.Payment({
		"intent": "sale",
		"payer": {
			"payment_method": "paypal",
		},
		"redirect_urls" : {
			"return_url" : "http://%s/feedly/execute" % server_host,
			"cancel_url" : "http://%s/feedly/cancel" % server_host
		},
		"transactions": [{
			"item_list":{ "items":items	},
			"amount": {
				"total": str(price),
				"currency": currency
			},
			"description": "Compra de Produtos na loja."
		}]
	})
	if payment.create(): return payment.id
	else: raise CheckoutError(payment.error)

def multiple_payment_handler(request, order_form, order):
	data = order_form.cleaned_data
	shipping = order.shipping_total
	code = CorreiosCode()
	shipping_data = code.consulta(order.billing_detail_postcode)[0]
	order.billing_detail_street  = '%s %s' % (shipping_data['Logradouro'],data['number_complement'])
	order.billing_detail_city    = shipping_data['Localidade']
	order.billing_detail_state   = shipping_data['UF']
	order.billing_detail_country = settings.STORE_COUNTRY
	order.save()
	cart = Cart.objects.from_request(request)
	currency = settings.SHOP_CURRENCY
	cart_items = []
	for item in cart.items.all():
		cart_items.append({
			"name":item.description,
			"sku":item.sku,
			"price":str(item.unit_price),
			"currency":currency,
			"quantity":item.quantity
		})
	cart_items.append({
		"name": "Frete via SEDEX",
		"sku":"1",
		"price":str(shipping),
		"currency":currency,
		"quantity":1
	})
	price = cart.total_price()+shipping

	if '1' in data['card_pay_option']:
		return paypal_payment(request,cart_items,price,currency)
	elif '2' in data['card_pay_option']:
		return pagseguro_payment(request,cart_items,price,order)

def pagseguro_payment(request,items,price,order):
	server_host = request.get_host()
	payment = pagseguro_api()
	for product in items:
		payment.add_item(id=product['sku'], 
        				 description=product['name'], 
        				 amount=product['price'], 
        				 quantity=product['quantity'])
	# Fixes problems in localhost development environment for PagSeguro checkout
	if 'localhost' in server_host or 'ubuntu' in server_host: server_host = settings.DEFAULT_HOST
	payment.redirect_url = "http://%s/feedly/execute" % server_host
	response = payment.checkout()
	order.pagseguro_redirect = response.payment_url
	order.save()
	return response.code