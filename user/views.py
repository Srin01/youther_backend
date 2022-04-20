from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.contrib.auth import get_user_model
from .renderers import UserJSONRenderer
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework import status
from core.pagination import FollowersLikersPagination
from user.serializers import UserInfoSerializer, RegisterUserSerializer, \
    UserProfileSerializer, FollowSerializer, LoginSerializer, UserSerializer, BalanceSerializer

class RegisterUserView(generics.CreateAPIView):
    serializer_class = RegisterUserSerializer
    permission_classes = (AllowAny,)


class LoginAPIView(APIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = LoginSerializer

    def post(self, request):
        user = request.data.get('user', {})

        # Notice here that we do not call `serializer.save()` like we did for
        # the registration endpoint. This is because we don't  have
        # anything to save. Instead, the `validate` method on our serializer
        # handles everything we need.
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class ManageUserView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserInfoSerializer

    def get_object(self):
        return self.request.user


class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = UserSerializer

    def retrieve(self, request, *args, **kwargs):
        # There is nothing to validate or save here. Instead, we just want the
        # serializer to handle turning our `User` object into something that
        # can be JSONified and sent to the client.
        serializer = self.serializer_class(request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        serializer_data = request.data.get('user', {})

        # Here is that serialize, validate, save pattern we talked about
        # before.
        serializer = self.serializer_class(
            request.user, data=serializer_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

class UserProfileView(generics.RetrieveAPIView):
    lookup_field = 'username'
    queryset = get_user_model().objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = (permissions.AllowAny,)


class BalanceView(viewsets.ModelViewSet):
    authentication_classes = [JSONWebTokenAuthentication]
    allowed_methods = ['get','post']
    serializer_class = BalanceSerializer

    def get_queryset(self):
        username = self.kwargs['username']
        queryset = get_user_model().objects.get(
            username=username)
        return queryset

    


class FollowUserView(APIView):

    def get(self, request, format=None, username=None):
        to_user = get_user_model().objects.get(username=username)
        from_user = self.request.user
        follow = None
        if from_user.is_authenticated:
            if from_user != to_user:
                if from_user in to_user.followers.all():
                    follow = False
                    from_user.following.remove(to_user)
                    to_user.followers.remove(from_user)
                else:
                    follow = True
                    from_user.following.add(to_user)
                    to_user.followers.add(from_user)
        data = {
            'follow': follow
        }
        return Response(data)


class GetFollowersView(generics.ListAPIView):
    serializer_class = FollowSerializer
    pagination_class = FollowersLikersPagination
    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
        username = self.kwargs['username']
        queryset = get_user_model().objects.get(
            username=username).followers.all()
        return queryset


class GetFollowingView(generics.ListAPIView):
    serializer_class = FollowSerializer
    pagination_class = FollowersLikersPagination
    # authentication_classes = [JWTAuthentication]
    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
        username = self.kwargs['username']
        queryset = get_user_model().objects.get(
            username=username).following.all()
        return queryset