from ecomap.model import *
import formencode
from formencode import validators
import cherrypy

def safe_get_element_child(root,name):
    v = ""
    if root.getElementsByTagName(name)[0].hasChildNodes():
        v = root.getElementsByTagName(name)[0].firstChild.nodeValue
    return v


def createTables():
    Ecouser.createTable(ifNotExists=True)
    Course.createTable(ifNotExists=True)
    Ecomap.createTable(ifNotExists=True)

def dropTables():
    Ecomap.dropTable(ifExists=True)
    Course.dropTable(ifExists=True)
    Ecouser.dropTable(ifExists=True)

class EcomapSchema(formencode.Schema):
    name         = validators.String(not_empty=True)
    description  = validators.String()
    owner        = validators.Int()
    course       = validators.Int()

class EcouserSchema(formencode.Schema):
    uni          = validators.String(not_empty=True)
    securityLevel= validators.Int()
    firstname    = validators.String()
    lastname     = validators.String()

class CourseSchema(formencode.Schema):
    name         = validators.String(not_empty=True)
    description  = validators.String()
    instructor   = validators.Int()

def setup_for_tests():
    dropTables()
    createTables()

def teardown_tests():
    dropTables()

def ldap_lookup(username):
    (lastname,firstname) = ("","")
    try:
        import ldap
        LDAP_SERVER = "ldap.columbia.edu"
        BASE_DN = "o=Columbia University, c=us"
        l = ldap.open(LDAP_SERVER)
        baseDN = BASE_DN
        searchScope = ldap.SCOPE_SUBTREE
        retrieveAttributes = None
        searchFilter = "uni=%s" % username
        ldap_result_id = l.search(baseDN, searchScope, searchFilter,
                                  retrieveAttributes)
        result_set = []
        while 1:
            result_type, result_data = l.result(ldap_result_id, 0)
            if result_data == []:
                break
            else:
                if result_type == ldap.RES_SEARCH_ENTRY:
                    values = result_data[0][1]
                    for k, v in values.items():
                        if k == 'sn':
                            lastname = v[0]
                        if k == 'givenname':
                            firstname = v[0]
    except ImportError:
        # no ldap library
        pass
    return (firstname,lastname)

def get_or_create_user(username,firstname="",lastname=""):
    """ if the user is already in the system, it returns the user object.
    otherwise, it creates a new one and returns that. the function has the
    side effect of putting the user into any class that wind says they
    should be a part of if they aren't already in it. """
    
    res = Ecouser.select(Ecouser.q.uni == username)
    u = None
    if res.count() > 0:
        # found the user. 
        u = res[0]
    else:
        #this user doesn't exist in our DB yet.  Get details from LDAP if possible
        (firstname,lastname) = ldap_lookup(username)
 	               
        if lastname == "":
            lastname = username
 	
        eus = EcouserSchema()
        d = eus.to_python({'uni' : username, 'securityLevel' : 2, 'firstname' : firstname, 'lastname' : lastname})
        u = Ecouser(uni=d['uni'],securityLevel=d['securityLevel'],firstname=d['firstname'],lastname=d['lastname'])
    return u

def get_user(username):
    res = Ecouser.select(Ecouser.q.uni == username)
    if res.count() > 0:
        return res[0]
    return None

def is_admin(username):
    res = Ecouser.select(Ecouser.q.uni == username)
    if res.count() > 0:
        if res[0].securityLevel == 1:
            return True
    return False

def is_instructor(username,course):
    if course.instructor.uni == username:
        return True
    return False
