#!/usr/bin/python
# -*- coding: utf-8 -*-
from app import Images,Spreads,Uploads
from content import Spreadables
from store import Store
from models import Product
from main import Efforia
from feedly.payments import Baskets

def efforia_main(request):
    e = Efforia()
    if request.method == 'GET':
        return e.start(request)

def spread_basket(request):
    b = Baskets(Product())
    if request.method == 'GET':
	   return b.view_items(request)
    elif request.method == 'POST':
	   return b.add_item(request)

def product_image(request):
    s = Store()
    if request.method == 'GET':
        return s.view_image(request)
    elif request.method == 'POST':
        return s.create_image(request)

def media(request):
    u = Uploads()
    if request.method == 'GET':
        return u.media_chooser(request)

def spreaded(request):
    s = Spreadables()
    if request.method == 'GET':
        return s.view_spreaded(request)

def spreadspread(request):
    s = Spreadables()
    if request.method == 'GET':
        return s.spreadspread(request)
    elif request.method == 'POST':
        return s.spreadobject(request)

def spreadable(request):
    s = Spreadables()
    if request.method == 'GET':
        return s.view_spreadable(request)
    
def playable(request):
    s = Spreadables()
    if request.method == 'GET':
        return s.view_playable(request)

def imageview(request):
    s = Spreadables()
    if request.method == 'GET':
        return s.view_images(request)

def image(request):
    i = Images()
    if request.method == 'GET':
        return i.view_image(request)
    elif request.method == 'POST':
        return i.create_image(request)
    
def upload(request):
    u = Uploads()
    if request.method == 'GET':
        return u.view_content(request)
    elif request.method == 'POST':
        return u.upload_content(request)

def init_spread(request):
    spread = Spreads()
    if request.method == 'GET':
        return spread.start_spreadapp(request)    

def main(request):
    graph = Spreads()
    if request.method == 'GET': 
        return graph.view_spread(request)
    elif request.method == 'POST': 
        return graph.create_spread(request)
    
def content(request):
    upload = Uploads()
    if request.method == 'GET':
        return upload.view_upload(request)

def store_main(request):
    prod = Store()
    if request.method == 'GET':
        return prod.view_product(request)
    elif request.method == 'POST':
        return prod.create_product(request)

def cancel(request):
    c = Cancel()
    if request.method == 'POST':
        return c.cancel(request)

def delivery(request):
    deliver = Deliveries()
    if request.method == 'GET':
        return deliver.view_package(request)
    elif request.method == 'POST':
        return deliver.create_package(request)

def mail(request):
    m = Mail()
    if request.method == 'GET':
        return m.postal_code(request)

def paypal_ipn(request):
    """Accepts or rejects a Paypal payment notification."""
    input = request.GET # remember to decode this! you could run into errors with charsets!
    if 'txn_id' in input and 'verified' in input['payer_status'][0]: pass
    else: raise Exception # Erro 402
