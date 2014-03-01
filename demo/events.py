from main import Efforia
from django.shortcuts import render
from django.http import HttpResponse as response
from django.conf import settings
from django.contrib.auth.models import User
from datetime import timedelta,date
from demo.models import Event,Sellable

class Events(Efforia):
    def __init__(self): pass
    def event_form(self,request):
        return render(request,'event.jade',{},content_type='text/html')
    def view_event(self,request,eventid):
        e = Event.objects.filter(id=eventid)[0]
        t = Sellable.objects.filter(sellid=eventid)
        sum = ratio = count = 0
        if len(t) > 0:
            for ticket in t: 
                if ticket.paid: sum += ticket.value; count += 1
            ratio = (float(sum)/float(e.value))*100.0
        permissions = self.verify_permissions(request)
        return render(request,'event.html',{
                       'perm':permissions,
                       'title':e.name[2:],
                       'ratio':ratio,
                       'buyers':count,
                       'event':e,
                       'static_url':settings.STATIC_URL
                       },content_type='text/html')
    def create_event(self,request):
        u = self.current_user(request)
        title = descr = local = max = min = value = dates = ''
        for k,v in request.REQUEST.iteritems():
            if 'name' in k: title = v
            elif 'description' in k: descr = v
            elif 'location' in k: local = v
            elif 'deadline' in k: dates = v
            elif 'min' in k: min = v
            elif 'value' in k: value = v#+int(float(v)*0.1)
        date = self.convert_datetime(dates)
        Event(name='@@%s'%title,user=u,deadline=date,description=descr,
        min=min,value=value,location=local).save()
        return render(request,'eventimage.jade',{'static_url':settings.STATIC_URL})
    def event_image(self,request):
        u = self.current_user(request)
        photo = request.FILES['Filedata'].read()
        dropbox = Dropbox()
        link = dropbox.upload_and_share(photo)
        res = self.url_request(link)
        e = Event.objects.filter(user=u).latest('date')
        e.visual = '%s?dl=1' % res
        e.save()
        return response(e.visual)
    def show_enroll(self,request):
        u = self.current_user(request)
        event = Event.objects.filter(user=u,id=request.REQUEST['id'])[0]
        return render(request,'enroll.jade',{'static_url':settings.STATIC_URL,'value':event.value})
    def event_id(self,request):
        u = self.current_user(request)
        e = list(Event.objects.filter(user=u))[0]
        e.event_id = request.REQUEST['id']
        e.save()
        return response('Event created successfully')
