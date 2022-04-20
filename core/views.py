from django.forms import modelformset_factory
from django.shortcuts import render
from requests import Response
from core.models import User
from core import models
from user import serializers
from rest_framework import  viewsets

# Create your views here.
class UserSQL(viewsets.ModelViewSet):
    # The usual stuff here
    model = models.User

    def list(self, request, *args,**kwarg):
        sqlQuery = request.GET.get('query')
        queryset = User.objects.raw(sqlQuery)
        serializer = serializers.UserInfoSerializer(queryset, many=True)
        return Response(serializer.data)