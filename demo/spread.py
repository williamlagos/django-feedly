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
from feedly.core import Feedly
from feedly.models import Basket

try:
    from paypal.standard.forms import PayPalPaymentsForm
    from paypal.standard.ipn.signals import payment_was_successful
except ImportError,e:
    pass

class Spreadables(Feedly):
    def __init__(self): pass
    def view_spreadable(self,request):
        spread_id = int(request.GET['id'])
        s = Spreadable.objects.filter(id=spread_id)[0]
        return render(request,'spreadview.jade',{'content':s.content,'spreadid':spread_id},content_type='text/html')
    def view_playable(self,request):
        playable_id = int(request.GET['id'])
        e = Playable.objects.filter(id=playable_id)[0]
        return render(request,'videoview.jade',{'playableid':playable_id},content_type='text/html')
    def view_images(self,request):
        image_id = int(request.GET['id'])
        i = Image.objects.filter(id=image_id)[0]
        return render(request,'imageview.jade',{'description':i.description,'image':i.link,'imageid':image_id},content_type='text/html')
    def spreadspread(self,request):
        return render(request,'spread.jade',{'id':request.GET['id']},content_type='text/html')
    def spreadobject(self,request):
        u = self.current_user(request)
        c = request.POST['content']
        spread = Spreadable(user=u,content=c,name='!'+u.username)
        spread.save()
        objid = request.POST['id']
        token = request.POST['token']
        s = Spreaded(name=token,spread=objid,spreaded=spread.id,user=u)
        s.save()
        return response('Spreaded object created successfully')
    def view_spreaded(self,request):
        spreadables = []; u = self.current_user(request)
        objid = request.GET['spreaded_id']
        token = request.GET['spreaded_token']
        typ,rel = self.object_token(token)
        sprdd = globals()[rel].objects.filter(spread=objid,name=token+'!')
        spreadables.append(globals()[typ].objects.filter(id=sprdd[0].spread)[0])
        for s in sprdd: spreadables.append(Spreadable.objects.filter(id=s.spreaded)[0])
        return self.view_mosaic(request,spreadables)

class Images(Feedly):
    def __init__(self): pass
    def view_image(self,request):
        return render(request,'image.jade',{'static_url':settings.STATIC_URL},content_type='text/html')
    def upload_image(self,request):
        photo = request.FILES['Filedata'].read()
        dropbox = Dropbox()
        link = dropbox.upload_and_share(photo)
        res = self.url_request(link)
        url = '%s?dl=1' % res
        return url
    def create_image(self,request):
        u = self.current_user(request)
        if 'description' in request.POST:
            image = list(Image.objects.filter(user=u))[-1:][0]
            descr = request.POST['description']
            image.description = descr
            image.save()
            return response('Description added to image successfully')
        i = Image(link=self.upload_image(request),user=u)
        i.save()
        return response('Image created successfully')

class Spreads(Feedly):
    def __init__(self): pass
    def start_spreadapp(self,request):
        return render(request,'spreadapp.jade',{'static_url':settings.STATIC_URL},content_type='text/html')
    def view_spread(self,request):
        return render(request,"spread.jade",{},content_type='text/html')
    def create_spread(self,request):
        u = self.current_user(request)
        name = u.first_name.lower()
        text = unicode('%s' % (request.POST['content']))
        post = Spreadable(user=u,content=text,name='!'+name)
        post.save()
        self.accumulate_points(1,request)
        return response('Spreadable created successfully')
    
class Uploads(Feedly):
    def __init__(self): pass
    def view_upload(self,request):
        return render(request,'content.jade',{'static_url':settings.STATIC_URL},content_type='text/html')
    def set_thumbnail(self,request):
        u = self.current_user(request)
        service = StreamService()
        token = request.GET['id']
        access_token = u.profile.google_token
        thumbnail = service.video_thumbnail(token,access_token)
        play = Playable.objects.filter(user=u).latest('date')
        play.visual = thumbnail
        play.token = token
        play.save()
        self.accumulate_points(1,request)
        r = redirect('/')
        r.set_cookie('token',token)
        return r
    def view_content(self,request):
        u = self.current_user(request)
        content = title = ''
        for k,v in request.REQUEST.iteritems(): 
            if 'title' in k: title = v
            elif 'content' in k: content = v
            elif 'status' in k: 
                return self.set_thumbnail(request)
        try: 
            url,token = self.parse_upload(request,title,content)
            return render(request,'video.jade',{'static_url':settings.STATIC_URL,
                                                  'hostname':request.get_host(),
                                                  'url':url,'token':token},content_type='text/html')
        except Exception: return response('Invalid file for uploading') 
    def parse_upload(self,request,title,content):
        keys = ','; keywords = content.split(' ')
        for k in keywords: k = normalize('NFKD',k.decode('utf-8')).encode('ASCII','ignore')
        keys = keys.join(keywords)
        playable = Playable(user=self.current_user(request),name='>'+title,description=content)
        playable.save()
        service = StreamService()
        access_token = self.current_user(request).profile.google_token
        return service.video_entry(title,content,keys,access_token)
    def media_chooser(self,request):
        return render(request,'chooser.jade')

class Store(Feedly):
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
