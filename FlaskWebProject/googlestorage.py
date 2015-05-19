from oauth2client.client import SignedJwtAssertionCredentials #localServer
from oauth2client.appengine import AppAssertionCredentials    #AppEngine
from httplib2 import Http
from apiclient.discovery import build                         #For ClientLibrary-API-access

from apiclient.http import MediaIoBaseUpload
from io import BytesIO

from config import _LOCAL_EXEC_, _PROJ_ID_, client_email_loc, client_email_glob, private_key_file


# TODO 
#   - handle Exceptions! [try: XXX except: client.AccessTokenRefreshError]
#   - specifi calls, such that API-calls can be taken with full arguments
#   - only create a storage_device if old one is expired, therfore more actions can be done with one device
#   - implement rest

def get_service(service_a,version_a,scope,local=False):
    def checkoutCredentials(scope,loc=False) :
        credentials = None
        if local :
            with open(private_key_file) as f:
                private_key = f.read()
            credentials = SignedJwtAssertionCredentials(client_email_loc, private_key,scope)
        else:
            credentials = AppAssertionCredentials(scope)
        return credentials
    credentials = checkoutCredentials(scope,loc=local)
    http_auth = credentials.authorize(Http()) 
    return build(service_a, version_a, http=http_auth)


# Variables
GS_service = 'storage'
GS_version = 'v1'
GS_scope = 'https://www.googleapis.com/auth/devstorage.read_write'

#
# BUCKET - schnittstelle [NoAccess]
#
def create_container(Bucket, public=True):
    raise NotImplementedError

def patch_container(Bucket):
    raise NotImplementedError

def update_container(Bucket):
    raise NotImplementedError

def delete_container(Bucket):
    raise NotImplementedError

def get_container(Bucket):
    storage = get_service(GS_service,GS_version,GS_scope,_LOCAL_EXEC_)
    req = storage.buckets().get(bucket=Bucket)
    return req.execute()

def list_container():
    storage = get_service(GS_service,GS_version,GS_scope,_LOCAL_EXEC_)
    req = storage.buckets().list(project=_PROJ_ID_)
    return req.execute()


#
#OBJECTS - schnittstelle [NoAccess]
#

def compose_object(): #compose META/MEDIA
    raise NotImplementedError
def copy_object(): #copy META/MEDIA
    raise NotImplementedError

def delete_object(Bucket,Filename):
    storage = get_service(GS_service,GS_version,GS_scope,_LOCAL_EXEC_)    
    req = storage.objects().delete(bucket=Bucket,object=Filename)
    return req.execute()

def get_object(Bucket, Filename, media=False): #get META/MEDIA
    storage = get_service(GS_service,GS_version,GS_scope,_LOCAL_EXEC_)    
    req = None
    if media :
        req = storage.objects().get_media(bucket=Bucket,object=Filename)
    else :
        req = storage.objects().get(bucket=Bucket,object=Filename)
    return req.execute() 

def insert_object(Bucket, Filename, File, FileMime='text/plain'): #insert META/MEDIA
    storage = get_service(GS_service,GS_version,GS_scope,_LOCAL_EXEC_)    
    
    FileObject = BytesIO(File)
    media_body = MediaIoBaseUpload(FileObject, mimetype=FileMime, resumable=True)  
    req = storage.objects().insert(bucket=Bucket,name=Filename,media_body=media_body)
    resp = None
    while resp is None :
        resp = req.next_chunk()
    return resp

def list_object(Bucket): # list/list_next
    storage = get_service(GS_service,GS_version,GS_scope,_LOCAL_EXEC_)    
    value = []
    fields_to_return = 'nextPageToken,items(name)'
    req = storage.objects().list(bucket=Bucket,fields=fields_to_return)
    while req is not None :
        resp = req.execute()
        value += [resp]
        req = storage.objects().list_next(req, resp)
    return value

def patch_object():  
    raise NotImplementedError
def rewrite_object():#rewrite META/MEDIA
    raise NotImplementedError
def update_object(): #update META/MEDIA
    raise NotImplementedError
def watchAll_object():
    raise NotImplementedError


#PROGRAM
# Implementation of Interface 'PythonStorage Interface' [General]

#GET
#http://[hostname]/storage/api/v1.0/[bucket_id]/files
def list_files(Bucket) :
    items = [str(k['name']) for k in list_object(Bucket)[0]['items']]
    return items

##GET
#http://[hostname]/storage/api/v1.0/[bucket_id]/files/[file_id]
def get_file(Bucket, FileName) :
    return get_object(Bucket, FileName,media=True)

##POST
##PUT
#http://[hostname]/storage/api/v1.0/[bucket_id]/files
#http://[hostname]/storage/api/v1.0/[bucket_id]/files/[file_id]
def put_file(File, Bucket, FileName) :
    return insert_object(Bucket,FileName,File)

#DELETE
#http://[hostname]/storage/api/v1.0/[bucket_id]/files/[file_id]
def delete_file(Bucket, FileName) :
    return delete_object(Bucket,FileName)



#
# DEBUGG - functions
#
def test_google_storage_handler() :
    value = ""
    value += "<br/>################### CONTAINER ##################<br/>"
    value += str(list_container())
    value += "<br/>################################################<br/>"

    value += "<br/>###################    id-0   ##################<br/>"
    value += str(get_container('id-0'))
    value += "<br/>################################################<br/>"

    value += "<br/>################### id-0 tmp.txt ###############<br/>"
    value += str(list_object('id-0'))
    value += "<br/>################################################<br/>"

    value += "<br/>################### id-0 tmp.txt ###############<br/>"
    value += str(get_object('id-0','tmp.txt'))
    value += "<br/>################################################<br/>"
    value += str(get_object('id-0','tmp.txt',media=True)) # now get File instead of META
    value += "<br/>################################################<br/>"

    value += "<br/>############# id-0 insert_test.txt #############<br/>"
    value += str(insert_object('id-0','tmp_media.txt','This is a Ludicrious Test, this should hopefully work'))
    value += "<br/>################################################<br/>"

    value += "<br/>############# id-0 replace_test.txt #############<br/>"
    value += str(insert_object('id-0','tmp_media.txt','This is a Ludicrious Test, this should hopefully work. [This is new Text by the Way]'))
    value += "<br/>################################################<br/>" 

    value += "<br/>############# id-0 remove_test.txt #############<br/>"
    value += str(delete_object('id-0','tmp_media.txt'))
    value += "<br/>################################################<br/>"
    return value

def test_google_storage_interface():
    _id_='id-demo'
    _file_ = 'dummy-file.txt'
    _content_ = 'Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.'[::-1]
    value = ""

    files = list_files(_id_)
    file_con = get_file(_id_,'tmp.txt')
    value += str(files)+"<br/>"+str(file_con)+"<br/><br/>"

    put_file(_content_,_id_,_file_) 
    files = list_files(_id_)
    file_con = get_file(_id_,_file_)
    value += str(files)+"<br/>"+str(file_con)+"<br/><br/>"
    
    delete_file(_id_,_file_)
    files = list_files(_id_)
    value += str(files)
    return value