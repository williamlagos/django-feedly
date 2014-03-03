#!/usr/bin/python
# -*- coding: utf-8 -*-
#from promote import Events,Promoteds,Projects,Movements
#from spread import Store,Spreadables,Images,Spreads,Uploads
from models import Product,Sellable
from feedly.payments import Baskets
from feedly.core import Feedly,user

def main(request):
    e = Feedly()
    if request.method == 'GET':
        return e.start(request)