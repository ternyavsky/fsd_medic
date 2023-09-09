from celery import group
from requests import api
from django.shortcuts import render 
from django.contrib.auth import logout
from django.http import Http404, HttpResponse
from django.core.cache import cache
from django.db.models import Prefetch
from db.queries import *
from api.permissions import *
from .models import Url_Params, Group
from .models import User, Like
from .permissions import IsAdminOrReadOnly
from .serializers import *
# REST IMPORTS
from rest_framework.views import APIView
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
import logging

from api import permissions


logger = logging.getLogger(__name__)

def index(request):
    return render(request, template_name='api/index.html')

def registration(request, parameter):
    if Url_Params.objects.filter(parameter=parameter).exists():
        group_id = Url_Params.objects.get(parameter=parameter).group_id
        group_name = Group.objects.get(id=group_id).name
        if group_name == 'Администраторы':
            return HttpResponse('Здесь будет форма регистрации админа')
        elif group_name == 'Администраторы Центров':
            return HttpResponse('Здесь будет форма регистрации центра и его админа')
        elif group_name == 'Администраторы Клиник':
            return HttpResponse('Здесь будет форма регистрации клиники и его админа')
        elif group_name == 'Врачи':
            return HttpResponse('Здесь будет форма регистрации врача')
    raise Http404

class SaveViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = SavedSerializer
    def get_queryset(self):
        data = cache.get_or_set("saved", get_saved())
        data.filter(user=self.request.user)
        logger.debug(self.request.path)
        return data

class LikeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = LikeSerializer
    
    def get_queryset(self):
        logger.debug(self.request.path)
        data = cache.get_or_set("likes", get_likes())
        data.filter(user=self.request.user)
        return data 


class NoteViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = NoteSerializer

    def get_queryset(self):
        data = cache.get_or_set("notes", get_notes()) 
        if not self.request.user.is_staff:
            data = data.filter(user=self.request.user)
            logger.debug(self.request.path)
            return data 
        return data
    

class NewsViewSet(viewsets.ModelViewSet):
    serializer_class = NewsSerializer

    def get_queryset(self):
        if self.action == 'list':
            data = cache.get_or_set("news", get_news())
            user = self.request.user
            if user.is_staff:
                logger.info("Admin request")
                return data

            if user.is_authenticated:
                try:
                    center_news = data.filter(center__in=user.center.all())
                    disease_news = data.filter(disease__in=user.disease.all())
                    data = center_news.union(disease_news)
                    logger.debug(self.request.path)
                    return data
                except:
                    logger.warning(self.request.path)
                    logger.info("Center or disease not specified!")
                    raise serializers.ValidationError("To access the news, you must specify the center or disease!")


            else:
                logger.warning("Not authorized")
                return data[:3]
        return get_news()

### SEARCH ###
class SearchView(APIView):

    def get(self, request, *args, **kwargs):
        clinics = cache.get_or_set("clinics", get_clinics())
        centers = cache.get_or_set("centers",get_centers())
        users = cache.get_or_set("users", get_users())
        doctors = users.filter(group__name="Врачи")
        search_results = {
            'clinics': clinics,
            'centers': centers,
            'users': doctors,
        }
        serializer = SearchSerializer(search_results) 
        logger.debug(serializer.data)
        logger.debug(request.path)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DoctorsListView(APIView):
    permissions_classes = [IsAuthenticated]
    def get(self,request):
        doc = cache.get_or_set("users", get_users())
        doctors =  doc.filter(group__name="Врачи", city=request.user.city)
        serializer = UserGetSerializer(doctors, many=True)
        logger.debug(serializer.data)
        logger.debug(request.path)
        return Response(serializer.data, status=status.HTTP_200_OK)

