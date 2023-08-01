from rest_framework import generics, viewsets
from django.shortcuts import render, redirect
from .models import Url_Params, Groups
from .serializers import *
from django.contrib import messages
from django.http import Http404, HttpResponse
from api.permissions import *
from .models import User, Like
from django.contrib.auth import logout
from .permissions import IsAdminOrReadOnly
# REST IMPORTS
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from db.queries import *



def index(request):
    return render(request, template_name='api/index.html')

def registration(request, parameter):
    if Url_Params.objects.filter(parameter=parameter).exists():
        group_id = Url_Params.objects.get(parameter=parameter).group_id
        group_name = Groups.objects.get(id=group_id).name
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
        return get_saved(user=self.request.user)

class LikeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = LikeSerializer
    
    def get_queryset(self):
        return get_likes(user=self.request.user)


class NoteViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = NoteSerializer

    def get_queryset(self):
        return get_notes(user=self.request.user) 
    

class NewsViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = NewsSerializer

    def get_queryset(self):
        if self.action == 'list':
            user = self.request.user
            if user.is_staff:
                return get_news()

            if user.is_authenticated:
                try:
                    center_news = get_news(center__in=user.center.all())
                    disease_news = get_news(disease__in=user.disease.all())
                    return center_news.union(disease_news)
                except:
                    raise serializers.ValidationError('Для доступа к новостям, вам следует указать центр или заболевание')

            else:
                return get_news()[:3]
        return get_news()

### SEARCH ###
class SearchView(APIView):
    def get(self, request, *args, **kwargs):
        clinics = get_clinics()
        centers = get_centers()
        users = get_users()
        search_results = {
            'clinics': clinics,
            'centers': centers,
            'users': users,
        }
        serializer = SearchSerializer(search_results)
        return Response(serializer.data, status=status.HTTP_200_OK)

class DoctorsListView(APIView):
    def get(self,request, *args, **kwargs):
        doc = get_users(group=get_groups(name="Врачи").first(), city=request.user.city)
        serializer = UserGetSerializer(doc, many=True)
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
