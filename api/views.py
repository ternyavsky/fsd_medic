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

from loguru import logger

logger.add("logs/api.log", format="{time} {level} {message}", level="DEBUG"  ,rotation="12:00", compression="zip")


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
        data = get_saved(user=self.request.user)
        logger.success(self.request.path)
        return data

class LikeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = LikeSerializer
    
    def get_queryset(self):
        logger.success(self.request.path)
        return get_likes(user=self.request.user)


class NoteViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = NoteSerializer

    def get_queryset(self):
        data = get_notes(user=self.request.user)
        logger.success(self.request.path)
        return data 
    

class NewsViewSet(viewsets.ModelViewSet):
    serializer_class = NewsSerializer

    def get_queryset(self):
        if self.action == 'list':
            user = self.request.user
            if user.is_staff:
                data = get_news()
                logger.info("Admin request")
                return data

            if user.is_authenticated:
                try:
                    center_news = get_news(center__in=user.center.all())
                    disease_news = get_news(disease__in=user.disease.all())
                    data = center_news.union(disease_news)
                    logger.success(self.request.path)
                    return data
                except:
                    logger.warning(self.request.path)
                    logger.info("Center or disease not specified!")
                    raise serializers.ValidationError("To access the news, you must specify the center or disease!")


            else:
                data = get_news()[:3]
                logger.warning("Not authorized")
                return data
        return get_news()

### SEARCH ###
class SearchView(APIView):

    def get(self, request, *args, **kwargs):
        clinics = get_clinics()
        centers = get_centers()
        users = get_users(group__name="Врачи")
        search_results = {
            'clinics': clinics,
            'centers': centers,
            'users': users,
        }
        serializer = SearchSerializer(search_results)
        logger.debug(serializer.data)
        logger.success(request.path)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DoctorsListView(APIView):
    def get(self,request):
        doc = get_users(group__name="Врачи", city=request.user.city)
        serializer = UserGetSerializer(doc, many=True)
        logger.debug(serializer.data)
        logger.success(request.path)
        return Response(serializer.data, status=status.HTTP_200_OK)

## Eclass UpdateUserView(generics.ListCreateAPIView):
#
#     permission_classes = [AllowAny]
#     model = User
#     serializer_class = CreateUserSerializer
#
#     def post(self, request):
#         serializer = CreateUserSerializer()
#         # serializer.update(instance=request.user, validated_data=request.data)
#         serializer.update(validated_data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
