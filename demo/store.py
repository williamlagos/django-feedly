#!/usr/bin/python
# -*- coding: utf-8 -*-
import json,time
from django.contrib.auth.models import User
from django.conf import settings
from django.http import HttpResponse as response
from django.http import HttpResponseRedirect as redirect
from django.shortcuts import render
from datetime import datetime

from demo.views import *
from demo.models import Product
from demo.app import Images
from feedly.models import Basket
from main import Efforia

try:
    from paypal.standard.forms import PayPalPaymentsForm
    from paypal.standard.ipn.signals import payment_was_successful
except ImportError,e:
    pass

class Cancel(Efforia):
    def __init__(self): pass
    def cancel(self,request):
        u = self.current_user(request)
        Cart.objects.all().filter(user=u).delete()
        self.redirect('/')
        #value = int(self.request.arguments['credit'])
        #self.current_user().profile.credit -= value
        #self.current_user().profile.save()

class Payments(Efforia):
    def __init__(self): pass
    def view_recharge(self,request):
        paypal_dict = {
            "business": settings.PAYPAL_RECEIVER_EMAIL,
            "amount": "1.19",
            "item_name": "Créditos do Efforia",
            "invoice": "unique-invoice-id",
            "notify_url": "http://www.efforia.com.br/paypal",
            "return_url": "http://www.efforia.com.br/",
            "cancel_return": "http://www.efforia.com.br/cancel",
            'currency_code': 'BRL',
            'quantity': '1'
        }
        payments = PayPalPaymentsForm(initial=paypal_dict)
        form = CreditForm()
        return render(request,"recharge.jade",{'form':payments,'credit':form},content_type='text/html')
    def update_credit(self,request):
        value = int(request.POST['credit'][0])
        current_profile = Profile.objects.all().filter(user=self.current_user(request))[0]
        if value > current_profile.credit: return self.view_recharge(request)
        else:
            current_profile.credit -= value
            current_profile.save()
            if 'other' in request.POST:
                iden = int(request.POST['other'][0])
                u = User.objects.all().filter(id=iden)[0]
                p = Profile.objects.all().filter(user=u)[0]
                p.credit += value
                p.save()
            self.accumulate_points(1,request)
            return response('')

class Store(Efforia):
    def __init__(self): pass
    def view_product(self,request):
        u = self.current_user(request)
        if 'action' in request.GET:
            deliver = list(Deliverable.objects.all().filter(buyer=u))
            if not len(deliver) or 'more' in request.GET:
                products = list(Product.objects.all())
                return self.render_grid(list(products),request)
            else: return self.render_grid(deliver,request)
        elif 'product' in request.GET:
            id = int(request.REQUEST['product'])
            prod = Product.objects.all().filter(id=id)[0]
            return render(request,'productview.jade',{'product':prod})
        else:
            return render(request,'product.jade',{'static_url':settings.STATIC_URL},content_type='text/html')
    def create_product(self,request):
        u = self.current_user(request)
        e = json.load(open('%s/json/elements.json'%settings.STATIC_ROOT))
        c = request.REQUEST['category']
        category = e['locale_cat'].index(c)
        credit = request.REQUEST['credit']
        name = request.REQUEST['name']
        description = request.REQUEST['description']
        product = Product(category=category,credit=credit,visual='',
        name='$$%s'%name,description=description,user=u)
        product.save()
        return redirect('productimage')
    def view_image(self,request):
        return render(request,'upload.jade',{'static_url':settings.STATIC_URL})
    def create_image(self,request):
        images = Images()
        u = self.current_user(request)
        url = images.upload_image(request)
        products = Product.objects.filter(user=u)
        latest = list(products)[-1:][0]
        latest.visual = url
        latest.save()
        return response("Product created successfully")
#payment_was_successful.connect(confirm_payment)
