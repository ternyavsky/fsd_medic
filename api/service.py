from rest_framework.response import Response
from rest_framework import status
def create_or_delete(classmodel, serializer, **kwargs):

    obj, created = classmodel.objects.get_or_create(**kwargs)

    if created:
        obj.save()
        return Response({'result': f'объект {classmodel.__name__} создан', 'data': serializer(obj).data}, status=status.HTTP_200_OK)
    else:
        obj.delete()
        return Response({'result': f'объект {classmodel.__name__} удален',  'data': serializer(obj).data}, status=status.HTTP_200_OK)