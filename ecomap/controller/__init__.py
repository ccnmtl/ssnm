from ecomap.model import *
from ecomap.helpers import *
from ecomap.helpers.cherrytal import CherryTAL
from ecomap.helpers import EcomapSchema
import ecomap.config as config

from cherrypy.lib import httptools
import cherrypy
import sys
import StringIO
import cgitb
import formencode
from formencode import validators
from formencode import htmlfill

DEBUG = True

def start(initOnly=False):
    environment = "development"
    if config.MODE == "production":
        environment = "production"

    cherrypy.root             = Eco()
    cherrypy.root.ecomap      = EcomapController()

    cherrypy.config.update({
        'global' : {
        'server.socketPort' : int(config.param('socketPort')),
        'server.threadPool' : int(config.param('threadPool')),
        'server.environment' : environment,
        'sessionFilter.on' : True,
        'sessionFilter.storageType' : "ram",
        },
        '/css' : {'staticFilter.on' : True, 'staticFilter.dir' : config.param('css')},
        '/images' : {'staticFilter.on' : True, 'staticFilter.dir' : config.param('images')},
        })
    cherrypy.server.start(initOnly=initOnly)



class EcoControllerBase(CherryTAL):
    _template_dir = "view"

    def referer(self):
        return cherrypy.request.headerMap.get('Referer','/')

    def _cpOnError(self):
        err = sys.exc_info()
        if DEBUG:
            sio = StringIO.StringIO()
            hook = cgitb.Hook(file=sio)
            hook.handle(info=err)            
            cherrypy.response.headerMap['Content-Type'] = 'text/html'
            cherrypy.response.body = [sio.getvalue()]
        else:
            # Do something else here.
            cherrypy.response.body = ['Error: ' + str(err[0])]


class Eco(EcoControllerBase):
    def index(self):
        # import pdb; pdb.set_trace()
        return "<h1>This is the main page</h1><p><a href='login'>Click here</a> to log in</p>"

    index.exposed = True

    def myList(self):

        #this is the list of ecomaps for the currently logged in user
        try:
            return self.template("list_ecomaps.pt",{'ecomaps' : [e for e in Ecomap.select(AND(Ecomap.q.ownerID == Ecouser.q.id, Ecouser.q.uni == cherrypy.session['UNI']))]})
        except:
            #right now, this means you're not logged in
            return httptools.redirect("/")
            #return "<a href='login'>Click here</a> to log in"
    myList.exposed = True

    def login(self,**kwargs):
        try:
            ticket_id = kwargs['ticketid']
        except:
            ticket_id = ""

        self.BASE_URL = cherrypy.request.base + "/login"

        if ticket_id == "":
            import urllib
            destination = urllib.quote(self.BASE_URL)
            url = "https://wind.columbia.edu/login?destination=%s&service=cnmtl_full_np" % destination
            httptools.redirect(url)
        else:
            (success,uni,groups) = validate_wind_ticket(ticket_id)
            if int(success) == 0:
                return uni # UNI is error message "WIND authentication failed. please try again or report this as a bug."

            cherrypy.session['UNI'] = uni
            cherrypy.session['Group'] = groups

            user = get_or_create_user(uni)
            print cherrypy.session['UNI']

            return "success!! %s logged in.  <a href='/myList'>click here</a> to go to list of ecomaps" % uni

    login.exposed = True


    def create_ecomap_form(self):
        defaults = {'name' : "x", 'description' : "y"}
        parser = htmlfill.FillingParser(defaults)
        parser.feed(self.template("create_ecomap.pt",{}))
        output = parser.text()
        parser.close()
        return output

    create_ecomap_form.exposed = True


    def create_ecomap(self,name="",description=""):

        es = EcomapSchema()

        try:
            ownerID = Ecouser.select(Ecouser.q.uni == cherrypy.session['UNI'])[0].id
            d = es.to_python({'name' : name, 'description' : description, 'owner' : ownerID})
            a = Ecomap(name=d['name'],description=d['description'],owner=d['owner'])
            return httptools.redirect("/myList")
        except formencode.Invalid, e:
            defaults = {'name' : name, 'description' : description}
            parser = htmlfill.FillingParser(defaults,errors=e.unpack_errors())
            parser.feed(self.template("create_ecomap.pt",{}))
            output = parser.text()
            parser.close()
            return output

    create_ecomap.exposed = True

    def update(self,**kwargs):
        #try:
            action = kwargs['action']
            if type(kwargs['ecomap_id']) is str:
                itemList = [int(kwargs['ecomap_id'])]
            elif type(kwargs['ecomap_id']) is list:
                itemList = [k for k in kwargs['ecomap_id']]
            else:
                output = "error - unknown argument type"

            if action == 'delete':
                while len(itemList) > 0:
                    item = itemList.pop()
                    self.ecomap = Ecomap.get(item)
                    self.ecomap.destroySelf()
            elif action == 'share':
                es = EcomapSchema()
                while len(itemList) > 0:
                    item = itemList.pop()
                    self.ecomap = Ecomap.get(item)
                    #d = es.to_python({'name' : name, 'description' : description, 'owner' : 1})
                    self.ecomap.public = not self.ecomap.public

            httptools.redirect("/myList")

        #except:
        #   return "no arguments"

    update.exposed = True



class EcomapController(EcoControllerBase):

    def index(self):
        return self.template("list_ecomaps.pt",{'ecomaps' : [e for e in Ecomap.select()]})
    index.exposed = True


    def default(self,ecomap_id,*args,**kwargs):
        ecomap_id = int(ecomap_id)
        self.ecomap = Ecomap.get(ecomap_id)
        if len(args) == 0:
            return self.view_ecomap(**kwargs)
        action = args[0]

        dispatch = {
            'delete' : self.delete,
            'edit_form' : self.edit_form,
            'edit' : self.edit,
            }
        if dispatch.has_key(action):
            return dispatch[action](**kwargs)
    default.exposed = True

    def edit_form(self):
        defaults = {'name' : self.ecomap.name, 'description' : self.ecomap.description}
        parser = htmlfill.FillingParser(defaults)
        parser.feed(self.template("edit_ecomap.pt",{'ecomap' : self.ecomap}))
        output = parser.text()
        parser.close()
        return output

    def edit(self,name="",description=""):
        es = EcomapSchema()
    #try:
        d = es.to_python({'name' : name, 'description' : description, 'owner' : self.ecomap.ownerID})
        self.ecomap.name = d['name']
        self.ecomap.description = d['description']
        return httptools.redirect("/ecomap/" + str(self.ecomap.id) + "/")
    #except formencode.Invalid, e:
        defaults = {'name' : name, 'description' : description}
        parser = htmlfill.FillingParser(defaults,errors=e.unpack_errors())
        parser.feed(self.template("edit_ecomap.pt",{'ecomap' : self.ecomap}))
        output = parser.text()
        parser.close()
        return output

    def view_ecomap(self,**kwargs):
        return self.template("view_ecomap.pt",{'ecomap' : self.ecomap})
    #ecomap.exposed = True


    def delete(self,confirm=""):
        #if confirm == "ok":
            self.ecomap.destroySelf()
            #cherrypy.session['message'] = "application deleted"
            return httptools.redirect("/myList")
        #else:
        #    return self.template("delete_ecomap.pt",{})


    #def update(self,**kwargs):
    #   return kwargs
    #update.exposed = True
		
		
		
		
