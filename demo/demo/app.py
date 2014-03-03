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
