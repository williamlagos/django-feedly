import re,difflib
from unicodedata import normalize
from datetime import datetime,timedelta
from django.shortcuts import render
from django.http import HttpResponse as response
from django.http import HttpResponseRedirect as redirect
from django.conf import settings

from feedly.core import user
from feedly.feed import Activity,Mosaic
from feedly.models import Profile,Sellable
from demo.models import Spreadable,Image,Playable,Spreaded,Product
from demo.models import Event,Project,Interest,Movement,Promoted

def sp(x): return '!!' in x[1]
def pl(x): return '>!' in x[1]
def im(x): return '%!' in x[1]

class Application(Activity):
    def __init__(self,user,app): 
        Activity.__init__(self,user,app)
    def deadline(self):
        playables = Playable.objects.filter(user=self.user)
        for play in playables:
            if not play.token and not play.visual: play.delete() 
    def relations(self,feed):
        excludes = []; rels = Spreaded.objects.filter(user=self.user)
        excludes.extend([(r.spreaded,'!!') for r in rels])
        excludes.extend([(r.spread,r.token()) for r in rels]) 
        for v in rels.values('spread').distinct():
            t = rels.filter(spread=v['spread'],user=self.user)
            if len(t) > 0: feed.append(t[len(t)-1])
        return excludes
    def duplicates(self,exclude,feed):
        for o in self.objects:
            objects = globals()[o].objects.filter(user=self.user)
            if 'Spreadable' in o: e = filter(sp,exclude)
            elif 'Playable' in o: e = filter(pl,exclude)
            elif 'Image' in o: e = filter(im,exclude)
            excludes = [x[0] for x in e]
            feed.extend(objects.exclude(id__in=excludes))

def ca(x): return '@#' in x[1]
def ev(x): return '@!' in x[1]

class PromoteApplication(Activity):
    def __init__(self,user,app):
        Activity.__init__(self,user,app)
    def verify_minimum(self,event,tickets):
        tickets_len = len(tickets)
        if event.min >= tickets_len: 
            event.occurred = True
            event.save()
    def increase(self,event,rate):
        if event.increased: return
        increase = event.value
        increase *= rate
        event.value += int(increase)
        event.increased = True
        event.save()
    def deadline(self):
        events = Event.objects.filter(user=self.user)
        for e in events:
            delta = e.remaining()
            if delta < 0:
                tickets = Sellable.objects.filter(sellid=e.id)
                if len(tickets): self.verify_minimum(e,tickets)
                if not e.occurred:
                    if e.postponed: self.return_funding(e,tickets)
                    e.deadline += timedelta(days=(-delta)/2)
                    e.postponed = True
                    e.save()
            elif delta < 5: self.increase(e,0.2)
            elif delta < 10: self.increase(e,0.1)
            else: pass
        projects = Project.objects.filter(user=self.user)
        for p in projects:
            if p.funded: continue 
            delta = p.remaining()
            # Projeto concluido, entrando para fila de movimentos
            if delta < 0:
                pledges = Sellable.objects.filter(sellid=p.id)
                move = Movement.objects.filter(cause=p)
                if len(pledges) > 0: self.verify_funding(p,pledges)
                if not p.funded:
                    p.date += timedelta(days=(-delta)/2)
                    if len(move) is 0: self.create_movement(p,self.user)
                    elif len(move) > 0: self.verify_movement(p,pledges)
            # Projeto ainda em andamento
            else: pass
    def relations(self,feed):
        excludes = []; rels = Promoted.objects.filter(user=self.user)
        excludes.extend([(r.prom,r.name) for r in rels]) 
        for v in rels.values('prom').distinct():
            t = rels.filter(prom=v['prom'],user=self.user)
            if len(t) > 0: feed.append(t[len(t)-1])
        return excludes
    def groupables(self,feed):
        movement = Movement.objects.filter(user=self.user)
        for v in movement.values('name').distinct():
            ts = movement.filter(name=v['name'],user=self.user)
            if len(ts): feed.append(ts[0])
    def duplicates(self,exclude,feed):
        for o in self.objects:
            objects = globals()[o].objects.filter(user=self.user)
            if 'Project' in o: e = filter(ca,exclude)
            elif 'Event' in o: e = filter(ev,exclude)
            excludes = [x[0] for x in e]
            feed.extend(objects.exclude(id__in=excludes))
    def verify_funding(self,project,pledges):
        pledge_sum = 0
        for p in pledges: pledge_sum += p.value
        if project.credit < pledge_sum:
            p = Profile.objects.filter(user_id=project.user_id)[0]
            p.coins += pledge_sum
            p.save()
            project.funded = True
            project.save()
    def verify_movement(self,project,pledges):
        elapsed = project.elapsed()
        final_d = project.deadline()+project.deadline()/2
        if elapsed > final_d:
            self.verify_funding(project,pledges)
            # Projeto nao financiado
            if not project.funded: self.return_funding(project,pledges)
    def create_movement(self,project,user):
        interests = Interest.objects.exclude(project=project).values()
        interest = Interest.objects.filter(project=project).values('key')[0]['key']
        m = Movement(name='##%s'%interest,user=user,cause=project)
        m.save()
        for k in interests:
            s = difflib.SequenceMatcher(None,interest,k['key'])
            if s.ratio() > 0.6:
                c = Project.objects.filter(id=k['project_id'])[0]
                m = Movement(name='##%s'%interest,user=user,cause=c)
                m.save()
    def return_funding(self,funding,pledges):
        funding.delete()
        for p in pledges: p.returnable = True; p.save()
    def return_pledges(self,project,pledges):
        for p in pledges:
            pro = Profile.objects.filter(user_id=p.backer_id)
            pro.coins += p.value
            pro.save()
            p.delete()
        project.delete()

