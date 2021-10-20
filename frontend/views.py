from django.http import response
from django.middleware.csrf import get_token
from django.http.response import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.core.files.images import get_image_dimensions
import json
from django.core import serializers

from frontend.models import *

# Function for get csrf token
# @author Luis GP
# @return json
def csrf(request):
    return HttpResponse(json.dumps({'csrftoken': get_token(request)}), content_type="application/json")




# Create your views here.
def index(request, *args, **kwargs):
    return render(request, 'frontend/index.html')




# This function recibes the user information and login to system
# @author Luis GP
# @return JSON
def authentication(request, *args, **kwargs):

    response = {}
    if request.method == "POST":

        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            response = {'status': 200, 'message': 'Now you are logged!', 'logged': True}

        else:
            response = {'status': 200, 'message': 'Wrong user or password!', 'logged': False}

    else:
        response = {'message': 'Wrong user or password!'}


    
    return HttpResponse(json.dumps(response), content_type="application/json")




def user_logout(request):
    logout(request)

    return HttpResponseRedirect(reverse('login_page'))




def islogged(request):
    # Code 0 is not logged
    # Code 1 is logged
    response = {'code': 0, 'message': 'The user is no logged'}
    if request.user is not None:
        response = {'code': 1, 'message': 'The user is logged'}

    return HttpResponse(json.dumps(response), content_type="application/json")




def getDirectory(request):

    response = {}
    
    if request.method == "POST" and 'route' in request.POST:
        
        id_current_folder = None

        if request.POST['route'] != "null":
            route = str(request.POST['route']).split('/')
            
            folder_route = '/'.join(route[:-2]) + "/"
            folder_name = route[-2]

            current_folder = Folder.objects.filter(folder_name=folder_name, folder_route=folder_route)
            if current_folder:
                id_current_folder = current_folder[0].id_folder

            folders = Folder.objects.filter(folder_route=request.POST['route'], deleted_at=None)
            files = File.objects.filter(file_route=request.POST['route'], deleted_at=None)

        else:
            folders = Folder.objects.filter(folder_route='./', deleted_at=None)
            files = File.objects.filter(file_route='./', deleted_at=None)
        
        folders = serializers.serialize('json', folders)
        files = serializers.serialize('json', files)

        response = {'files': files, 'folders': folders, 'id_current_folder': id_current_folder}

    else:
        response = {"status": 200, "message": "Invalid data!"}


    return HttpResponse(json.dumps(response), content_type="application/json")




def createNewFolder(request):
    response = {}

    try:
        folder = Folder()
        folder_route = './'
        if 'id_folder' in request.POST and request.POST['id_folder'] != "":
            folder.id_parent_folder = request.POST['id_folder']
            parent = Folder.objects.get(pk=request.POST['id_folder'])
            folder_route = parent.folder_route + parent.folder_name + "/"
        
        folder.id_user = request.user.id
        folder.folder_name = request.POST['folder_name']
        folder.folder_route = folder_route

        #folder.save()
    
        response = {'status': 200, 'message': f'The folder "{folder.folder_name}" was created!'}

    except Exception as e:
        response = {'status': 500, 'message': f'Error: {e}'}
    

    return HttpResponse(json.dumps(response), content_type="application/json")




def uploadFiles(request):
    response = {}

    try:
        if request.user is not None:
            for index, filename in request.FILES.items():

                file = request.FILES[index]
                f = File()

                id_folder = request.POST['id_folder'] if request.POST['id_folder'] != 'null' else None
                folder = Folder.objects.filter(id_folder=id_folder).first()
                extension = str(filename).split('.')[-1]

                f.id_folder = id_folder
                f.file_route = request.POST['route']
                f.id_user = request.user.id
                f.file_extension = extension
                f.file_name = filename
                f.file = file

                if folder:
                    url = str(folder.folder_route).replace("./", '') + folder.folder_name
                    f.file_url = f'/media/storage/{request.user}/{url}/{filename}'
                else:
                    f.file_url = f'/media/storage/{request.user}/{filename}'


                if extension in ['jpg','jpge','png','gif']:
                    width, height = get_image_dimensions(file)
                    f.img_width = width
                    f.img_height = height

                    if height > width:
                        f.orientation = "v"
                    else:
                        f.orientation = "h"
                    
                f.save()

        
        response = {'status': 200, 'message': 'Files has been uploaded!'}
    except Exception as e:
        response = {'status': 500, 'message': f'Cannot upload files! E:{e}'}


    return HttpResponse(json.dumps(response), content_type="application/json")