import random,re
from datetime import datetime
from difflib import SequenceMatcher
from django.shortcuts import render
from django.http import HttpResponse as response
from django.http import HttpResponseRedirect as redirect
from django.conf import settings

from main import Efforia
from demo.models import Sellable,Promoted,Interest,Movement,Project

class Projects(Efforia):
    def __init__(self): pass
    def start_promoteapp(self, request):
        return render(request, "createapp.jade", {'static_url':settings.STATIC_URL}, content_type='text/html')
    def project_form(self, request):
        return render(request,'project.jade',{},content_type='text/html')
    def view_backers(self,request):
        backers = []; u = self.current_user(request)
        pledge = Sellable.objects.filter(sellid=request.GET['project_id'])
        for p in pledge: backers.append(p.backer.profile)
        return self.view_mosaic(request,backers)
    def view_project(self,request,projectid):
        backers = set([])
        project = Project.objects.filter(id=projectid)[0]
        pledges = Sellable.objects.filter(sellid=projectid)
        ratio = sum = count = 0
        if len(pledges) > 0:
            for d in pledges: 
                if d.paid: sum += d.value; count += 1
            ratio = (float(sum)/float(project.credit))*100.0
        remaining = abs(project.remaining())
        permissions = self.verify_permissions(request)
        return render(request,'project.html',{
                                                  'perm':permissions,
                                                  'project':project,
                                                  'ratio':ratio,
                                                  'remaining':remaining,
                                                  'backers':count},content_type='text/html')
    def create_project(self, request):
        u = self.current_user(request)
        n = t = e = key = ''; c = 0
        for k, v in request.POST.items():
            if 'title' in k: n = '#%s' % v.replace(" ", "")
            elif 'credit' in k: c = v#+int(float(v)*0.1)
            elif 'content' in k: t = v
            elif 'deadline' in k: e = datetime.strptime(v, '%d/%m/%Y')
            elif 'keyword' in k: key = v
        project = Project(name=n,user=u,content=t,end_time=e,credit=int(c))
        project.save()
        interest = Interest(project=project,key=key)
        interest.save()
        service = StreamService()
        access_token = u.profile.google_token
        t = re.compile(r'<.*?>').sub('', t)
        url, token = service.video_entry(n[:1], t, 'efforia', access_token)
        return render(request, 'projectvideo.jade', {'static_url':settings.STATIC_URL,
                                            'hostname':request.get_host(),
                                            'url':url, 'token':token}, content_type='text/html')
    def view_pledge(self,request):
        ident = request.REQUEST['id'] 
        value = Project.objects.filter(id=ident)[0].credit
        pledges = Sellable.objects.filter(sellid=ident)
        sum = 0
        for p in pledges: sum += p.value
        difference = value-sum
        if difference < 0: difference = 0
        return render(request,'pledge.jade',{'value':difference},content_type='text/html')
    def link_project(self, request):
        u = self.current_user(request)
        token = request.GET['id']
        service = StreamService()
        access_token = u.profile.google_token
        thumbnail = service.video_thumbnail(token, access_token)
        project = Project.objects.filter(user=u).latest('date')
        project.visual = thumbnail
        project.ytoken = token
        project.save()
        return redirect('/')

class Movements(Efforia):
    def __init__(self): pass
    def movement_form(self,request):
        Interests = []
        for key in Interest.objects.all().values('key'): 
            Interests.append(key['key'])
        random.shuffle(Interests) 
        return render(request,'movement.jade',{'keys':Interests[:10],'quantity':len(Interests)},content_type='text/html')
    def view_movement(self,request):
        u = self.current_user(request)
        move = Movement.objects.filter(user=u); feed = []
        name = '##%s' % request.GET['title'].rstrip()
        for m in move.filter(name=name): feed.append(m.cause)
        return self.view_mosaic(request,feed)
    def create_movement(self,request):
        u = self.current_user(request)
        title = request.POST['title']
        key = request.POST['interest']
        p = Interest.objects.filter(key=key)[0].project
        interests = Interest.objects.exclude(project=p).values()
        interest = Interest.objects.filter(project=p).values('key')[0]['key']
        m = Movement(name='##%s'%title,user=u,cause=p)
        m.save()
        for k in interests:
            s = SequenceMatcher(None,interest,k['key'])
            if s.ratio() > 0.6:
                c = Project.objects.filter(id=k['project_id'])[0]
                m = Movement(name='##%s'%title,user=u,cause=c)
                m.save()
        return response('Movement created successfully')
