import uuid
import os
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


def image_file_path(instance, filename):
    """Generate file path for new recipe image"""
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'

    return os.path.join('uploads/', filename)


class UserManager(BaseUserManager):

    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        if not username:
            raise ValueError('Users must have a username')
        user = self.model(email=self.normalize_email(email),
                          username=username.lower(),
                          **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, username, password):
        user = self.create_user(email, username, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class Hobby(models.Model):
    idhobby = models.AutoField(primary_key=True)
    hobbyname = models.CharField(db_column='hobbyName', max_length=45)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'hobby'

class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    fullname = models.CharField(max_length=60, blank=True)
    bio = models.TextField(blank=True)
    profile_pic = models.ImageField(
        upload_to=image_file_path,
        default='avatar.png')
    followers = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                       related_name="user_followers",
                                       blank=True,
                                       symmetrical=False)
    following = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                       related_name="user_following",
                                       blank=True,
                                       symmetrical=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    hobbies = models.ManyToManyField(Hobby, related_name='user_hobbies')

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def number_of_followers(self):
        if self.followers.count():
            return self.followers.count()
        else:
            return 0

    def number_of_following(self):
        if self.following.count():
            return self.following.count()
        else:
            return 0

    def __str__(self):
        return self.username


class Transaction(models.Model):
    idtransaction = models.AutoField(db_column='idTransaction', primary_key=True)  # Field name made lowercase.
    transactionamount = models.FloatField(db_column='TransactionAmount', blank=True, null=True)  # Field name made lowercase.
    transactionresult = models.CharField(db_column='TransactionResult', max_length=45, blank=True, null=True)  # Field name made lowercase.
    user_idbuyer = models.ForeignKey('User', models.DO_NOTHING, db_column='user_idBuyer', related_name = 'buyer')  # Field name made lowercase.
    user_idseller = models.ForeignKey('User', models.DO_NOTHING, db_column='user_idSeller', related_name = 'seller')  # Field name made lowercase.
    post = models.ForeignKey('Post',
                             on_delete=models.CASCADE,
                             related_name='post_transaction')

    class Meta:
        managed = True
        db_table = 'transaction'


class Post(models.Model):
    id = models.UUIDField(primary_key=True,
                          default=uuid.uuid4,
                          editable=False)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='user_posts'
    )
    posttype = models.CharField(db_column='PostType', max_length=45, blank=True, null=True)
    photo = models.ImageField(
        upload_to=image_file_path,
        blank=False,
        editable=False)
    text = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    posted_on = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                   related_name="likers",
                                   blank=True,
                                   symmetrical=False)

    class Meta:
        ordering = ['-posted_on']
        db_table = 'post'

    def number_of_likes(self):
        if self.likes.count():
            return self.likes.count()
        else:
            return 0

    def __str__(self):
        return f'{self.author}\'s post'


class Comment(models.Model):
    idcomment = models.AutoField(db_column='idComment', primary_key=True)
    post = models.ForeignKey('Post',
                             on_delete=models.CASCADE,
                             related_name='post_comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=models.CASCADE,
                               related_name='user_comments')
    text = models.CharField(max_length=100)
    posted_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-posted_on']
        db_table = 'comment'

    def __str__(self):
        return f'{self.author}\'s comment'


