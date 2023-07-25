from rest_framework import generics, viewsets
from django.shortcuts import render, redirect

from .models import Url_Params, Groups

from .serializers import *

from django.contrib import messages
from django.http import Http404, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import User, Like
from django.contrib.auth import logout
from api.service import create_or_delete
from .permissions import IsAdminOrReadOnly
from django.shortcuts import get_object_or_404
# REST IMPORTS
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from db.queries import *

from api import permissions

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



### NEWS BLOCK ###



class SaveView(generics.ListCreateAPIView):
    permission_classes  = [IsAuthenticated]
    queryset = Saved.objects.all()

    def get(self, request):
        saved = self.queryset.filter(user=request.user)
        serializer = SavedSerializer(saved, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        try:
            return create_or_delete(Saved, SavedSerializer, user=request.user, news=get_news(id=request.data["news"]))
        except:
            return Response({'error': 'Запись не найдена!'}, status=status.HTTP_404_NOT_FOUND)



class LikeView(APIView):  # Append and delete like
    queryset = Like.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request):
        like = self.queryset.filter(user=request.user)
        serializer = LikeSerializer(like, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        try:
            return create_or_delete(Like, LikeSerializer, user=request.user, news=get_news(id=request.data["news"]))
        except:
            return Response({'error': 'Запись не найдена!'}, status=status.HTTP_404_NOT_FOUND)


class NewsDetailView(APIView):  # Single news view
    permission_classes = [IsAdminOrReadOnly]
    error_response = {'error': 'Новость не найдена!'}

    def get(self, request, id):  # get single news
        news = get_news(id=id)
        serializer = NewsSerializer(news)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, id):  # delete single news
        news = get_news(id=id)
        news.delete()
        return Response({'result': 'Новость удалена!'}, status=status.HTTP_204_NO_CONTENT)

    def put(self, request, id):  # update single news
        news = get_news(id=id)
        serializer = CreateNewsSerializer(news, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    def handle_exception(self, exc):
        if isinstance(exc, Http404):
            return Response(self.error_response, status=status.HTTP_404_NOT_FOUND)
        return super().handle_exception(exc)


class NewsView(generics.ListCreateAPIView):
    permission_classes = [AllowAny]  # Only authenticated users can access all news
    serializer_class = NewsSerializer

    def get_queryset(self):
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



    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = NewsSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


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

class NoteView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        notes = get_notes(user=request.user)
        serializer = NoteSerializer(notes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CreateNoteSerializer(data=request.data, context={'request':request})
        print(request.user, 'from views')
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class NoteDetailView(APIView):
   # permission_classes = [IsAuthenticated]
    def get(self, request, note_id):
        obj = get_notes(id=note_id)
        serializer = NoteSerializer(obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, note_id):
        obj = get_notes(id=note_id)
        serializer = NoteUpdateSerializer(instance=obj, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(NoteSerializer(obj).data, status=status.HTTP_200_OK)

    def delete(self, request, note_id):
        obj = get_notes(id=note_id)
        obj.delete()
        return Response({'result': 'deleted'}, status=status.HTTP_204_NO_CONTENT )




class UserDetailView(generics.RetrieveUpdateAPIView):
    """Получение, редактирование отдельного пользователя по id"""
    serializer_class = UserGetSerializer
    queryset = get_users()

## END USERS' CLASSES ###



class GetDiseasesView(APIView):
    def get(self, request):
        diseases = get_disease()
        serializer = DiseaseSerializer(diseases, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# class UpdateUserView(generics.ListCreateAPIView):
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


def LOGOUT(request):
    logout(request)
    return redirect('home_url')


@csrf_exempt
def LIKE(request, news_id):
    if request.user.is_active:
        if request.method == 'POST':
            create_or_delete(Like, news=news_id, user=request.user)
            return redirect('home_url')
        else:
            messages.error(request, 'Ошибка!')
    else:
        raise Http404


def Account(request):
    if request.user.is_active:
        return render(request, template_name='api/AccountView.html',
                      context={'title': 'Аккаунт', 'user': request.user})
    else:
        raise Http404
