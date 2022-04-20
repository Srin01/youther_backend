from django.contrib.auth import get_user_model
from core.models import Transaction, User
from rest_framework import serializers
from core.models import Post, Comment
from django.core.paginator import Paginator
from rest_framework.settings import api_settings
from django.contrib.auth import authenticate


class RegisterUserSerializer(serializers.ModelSerializer):
    """Serializer for creating a new user account"""

    class Meta:
        model = get_user_model()
        fields = ('id', 'email', 'fullname', 'username', 'password')
        extra_kwargs = {'password': {'write_only': True,
                                     'min_length': 5},
                        'username': {'min_length': 3}}

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        return get_user_model().objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255)
    username = serializers.CharField(max_length=255, read_only=True)
    password = serializers.CharField(max_length=128, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        # The `validate` method is where we make sure that the current
        # instance of `LoginSerializer` has "valid". In the case of logging a
        # user in, this means validating that they've provided an email
        # and password and that this combination matches one of the users in
        # our database.
        email = data.get('email', None)
        password = data.get('password', None)

        # Raise an exception if an
        # email is not provided.
        if email is None:
            raise serializers.ValidationError(
                'An email address is required to log in.'
            )

        # Raise an exception if a
        # password is not provided.
        if password is None:
            raise serializers.ValidationError(
                'A password is required to log in.'
            )

        # The `authenticate` method is provided by Django and handles checking
        # for a user that matches this email/password combination. Notice how
        # we pass `email` as the `username` value since in our User
        # model we set `USERNAME_FIELD` as `email`.
        user = authenticate(username=email, password=password)

        # If no user was found matching this email/password combination then
        # `authenticate` will return `None`. Raise an exception in this case.
        if user is None:
            raise serializers.ValidationError(
                'A user with this email and password was not found.'
            )

        # Django provides a flag on our `User` model called `is_active`. The
        # purpose of this flag is to tell us whether the user has been banned
        # or deactivated. This will almost never be the case, but
        # it is worth checking. Raise an exception in this case.
        if not user.is_active:
            raise serializers.ValidationError(
                'This user has been deactivated.'
            )

        # The `validate` method should return a dictionary of validated data.
        # This is the data that is passed to the `create` and `update` methods
        # that we will see later on.
        return {
            'email': user.email,
            'username': user.username,
            'token': user.token
        }


class UserInfoSerializer(serializers.ModelSerializer):
    """Serializer for the user settings objects"""

    class Meta:
        model = get_user_model()
        fields = ('id', 'email', 'username', 'password',
                  'fullname', 'bio', 'profile_pic')
        extra_kwargs = {'password': {'write_only': True,
                                     'min_length': 5},
                        'username': {'min_length': 3}}

    def update(self, instance, validated_data):
        """Update a user, setting the password correctly and return it"""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class UserPostsSerializer(serializers.ModelSerializer):
    """Serializer for viewing a user posts"""
    number_of_comments = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('id', 'photo', 'text', 'location', 'number_of_likes',
                  'number_of_comments', 'posted_on')

    def get_number_of_comments(self, obj):
        return Comment.objects.filter(post=obj).count()


class UserSerializer(serializers.ModelSerializer):
    """Handles serialization and deserialization of User objects."""

    # Passwords must be at least 8 characters, but no more than 128 
    # characters. These values are the default provided by Django. We could
    # change them, but that would create extra work while introducing no real
    # benefit, so lets just stick with the defaults.
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )

    class Meta:
        model = get_user_model()
        fields = ('email', 'username', 'password', 'token',)

        # The `read_only_fields` option is an alternative for explicitly
        # specifying the field with `read_only=True` like we did for password
        # above. The reason we want to use `read_only_fields` here is that
        # we don't need to specify anything else about the field. The
        # password field needed the `min_length` and 
        # `max_length` properties, but that isn't the case for the token
        # field.
        read_only_fields = ('token',)


    def update(self, instance, validated_data):
        """Performs an update on a User."""

        # Passwords should not be handled with `setattr`, unlike other fields.
        # Django provides a function that handles hashing and
        # salting passwords. That means
        # we need to remove the password field from the
        # `validated_data` dictionary before iterating over it.
        password = validated_data.pop('password', None)

        for (key, value) in validated_data.items():
            # For the keys remaining in `validated_data`, we will set them on
            # the current `User` instance one at a time.
            setattr(instance, key, value)

        if password is not None:
            # `.set_password()`  handles all
            # of the security stuff that we shouldn't be concerned with.
            instance.set_password(password)

        # After everything has been updated we must explicitly save
        # the model. It's worth pointing out that `.set_password()` does not
        # save the model.
        instance.save()

        return instance


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for viewing a user profile"""
    number_of_posts = serializers.SerializerMethodField()
    followed_by_req_user = serializers.SerializerMethodField()
    user_posts = serializers.SerializerMethodField('paginated_user_posts')

    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'fullname',
                  'bio', 'profile_pic', 'number_of_followers',
                  'number_of_following', 'number_of_posts',
                  'user_posts', 'followed_by_req_user')

    def get_number_of_posts(self, obj):
        return Post.objects.filter(author=obj).count()

    def paginated_user_posts(self, obj):
        page_size = 1
        paginator = Paginator(obj.user_posts.all(), page_size)
        page = self.context['request'].query_params.get('page') or 1

        user_posts = paginator.page(page)
        serializer = UserPostsSerializer(user_posts, many=True)

        return serializer.data

    def get_followed_by_req_user(self, obj):
        user = self.context['request'].user
        return user in obj.followers.all()


class FollowSerializer(serializers.ModelSerializer):
    """Serializer for listing all followers"""

    class Meta:
        model = get_user_model()
        fields = ('username', 'profile_pic')

class BalanceSerializer(serializers.ModelSerializer):
    """Serializer for listing balance"""

    class Meta:
        model = get_user_model()
        fields = ('username', 'account_balance')

class TransactionSerializer(serializers.ModelSerializer):
    """Serializer for listing balance"""

    class Meta:
        model = Transaction
        fields = ('idtransaction', 'transactionamount', 'transactionresult', 'user_idbuyer', 'user_idseller', 'post')

    def get_user_idbuyer(self, obj):
        return User.objects.filter(id=obj)

