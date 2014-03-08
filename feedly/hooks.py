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

try:
	from mezzanine.conf import settings
	from cartridge.shop.forms import OrderForm
	from cartridge.shop.models import Cart
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
	pass

def paypal_payment_handler(request, order_form, order):
	paypal_api()
	data = order_form.cleaned_data
	print data
	print order
	cart = Cart.objects.from_request(request)
	order.total = cart.total_price()
	print cart.total_price()
	print cart.total_quantity()
	locale.setlocale(locale.LC_ALL, settings.SHOP_CURRENCY_LOCALE)
	currency = locale.localeconv()
	currency_code = currency['int_curr_symbol'][0:3]
 
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
			"amount": {
				"total": str(order.total),
				"currency": currency_code
			},
			"description": "Compra de Produtos na loja."
		}]
	})
	if payment.create(): return payment.id
	else: raise CheckoutError(payment.error)

def pagseguro_payment_handler(request, order_form, order):
	pagseguro_api()
	print order_form
	print order
	return response('Hello World!')

def multiple_payment_handler(request, order_form, order):
	pass