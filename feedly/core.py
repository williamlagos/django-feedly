from django.contrib.auth.models import User
from django.conf import settings
from django.shortcuts import render

from feed import Mosaic

def user(name): return User.objects.filter(username=name)[0]
def superuser(): return User.objects.filter(is_superuser=True)[0]

class Feedly(Mosaic):
    def __init__(self): pass
    def verify_permissions(self,request):
        perm = 'super'
        if 'permissions' in request.COOKIES:
            perm = request.COOKIES['permissions']
        permissions = True if 'super' in perm else False
        return permissions
    def start(self,request):
        # Painel do usuario
        u = user('efforia'); 
        permissions = self.verify_permissions(request)
        actions = settings.EFFORIA_ACTIONS; apps = []
        for a in settings.EFFORIA_APPS: apps.append(actions[a])
        return render(request,'interface.html',{'static_url':settings.STATIC_URL,
                                            'user':user('efforia'),'perm':permissions,
                                            'name':'%s %s' % (u.first_name,u.last_name),'apps':apps
                                            },content_type='text/html')
        # Pagina inicial
        #p = list(Page.objects.filter(user=superuser()))
        #return render(request,'index.html',{'static_url':settings.STATIC_URL},content_type='text/html')
    def external(self,request):
        u = self.current_user(request)
        sellables = Sellable.objects.filter(user=u)
        for s in sellables: s.paid = True
        return self.redirect('/')
    def profile_view(self,request,name):
        if len(list(User.objects.filter(username=name))) > 0: request.session['user'] = name
        r = redirect('/')
        r.set_cookie('permissions','view_only')
        return r
    def json_decode(self,string):
        j = json.loads(string,'utf-8')
        return ast.literal_eval(j)
    def url_request(self,url,data=None,headers={}):
        request = urllib2.Request(url=url,data=data,headers=headers)
        request_open = urllib2.urlopen(request)
        return request_open.geturl()
    def do_request(self,url,data=None,headers={}):
        response = ''
        request = urllib2.Request(url=url,data=data,headers=headers)
        try:
            request_open = urllib2.urlopen(request)
            response = request_open.read()
            request_open.close()
        except urllib2.HTTPError,e:
            print url
            print data
            print headers
            print e.code
            print e.msg
            print e.hdrs
            print e.fp
        return response
    def object_token(self,token):
        relations = settings.EFFORIA_TOKENS
        typobject = relations[token]
        return typobject
    def object_byid(self,token,ident):
        obj = self.object_token(token)
        return globals()[obj].objects.filter(id=ident)[0]
    def convert_datetime(self,date_value):
        d = time.strptime(date_value,'%d/%m/%Y')
        return datetime.fromtimestamp(time.mktime(d))
    def authenticate(self,username,password):
        exists = User.objects.filter(username=username)
        if exists:
            if exists[0].check_password(password): 
                return exists
        else: return None
    def authenticated(self):
        name = self.get_current_user()
        if not name: 
            #self.redirect('login')
            self.render('templates/enter.html',STATIC_URL=settings.STATIC_URL)
            return False
        else:
            return True
    def accumulate_points(self,points,request=None):
        if request is None: u = self.current_user()
        else: u = self.current_user(request)
        current_profile = Profile.objects.all().filter(user=u)[0]
        current_profile.points += points
        current_profile.save()
