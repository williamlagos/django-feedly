from django.shortcuts import render
from django.http import HttpResponse as response
from django.conf import settings

from demo.models import Spreadable,Image,Playable,Spreaded,Promoted,Movement,Project,Event
from main import Efforia

class Spreadables(Efforia):
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

class Promoteds(Efforia):
    def promote_form(self,request):
        return render(request,'promote.jade',{},content_type='text/html')
    def promote(self,request):
        u = self.current_user(request)
        for k,v in request.REQUEST.iteritems():
            if 'content' in k: content = v
            elif 'id' in k: promotedid = v
            elif 'token' in k: token = v
        move = Movement.objects.filter(cause_id=promotedid)
        if len(move) > 0: p = Promoted(name='$#',prom=promotedid,content=content,user=u); p.save()
        else: s = Promoted(name=token,prom=promotedid,content=content,user=u); s.save() 
        mod,pobj = settings.EFFORIA_TOKENS[token].split('.')
        o = globals()[pobj].objects.filter(id=promotedid)[0]
        return response(o.event_id)
    def promoted(self,request):
        u = self.current_user(request)
        ident = request.REQUEST['id']
        p = Promoted.objects.filter(prom=ident)
        mod,pobj = settings.EFFORIA_TOKENS[p[0].name].split('.')
        o = globals()[pobj].objects.filter(id=ident)[0]
        feed = list(p); feed.append(o)
        return self.view_mosaic(request,feed)
