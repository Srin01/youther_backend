# Generated by Django 3.2.3 on 2022-02-27 07:14

import core.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(max_length=30, unique=True)),
                ('email', models.EmailField(max_length=255, unique=True)),
                ('fullname', models.CharField(blank=True, max_length=60)),
                ('bio', models.TextField(blank=True)),
                ('profile_pic', models.ImageField(default='avatar.png', upload_to=core.models.image_file_path)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('date_joined', models.DateTimeField(auto_now_add=True)),
                ('followers', models.ManyToManyField(blank=True, related_name='user_followers', to=settings.AUTH_USER_MODEL)),
                ('following', models.ManyToManyField(blank=True, related_name='user_following', to=settings.AUTH_USER_MODEL)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Hobby',
            fields=[
                ('idhobby', models.AutoField(primary_key=True, serialize=False)),
                ('hobbyname', models.CharField(db_column='hobbyName', max_length=45)),
            ],
            options={
                'db_table': 'hobby',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('posttype', models.CharField(blank=True, db_column='PostType', max_length=45, null=True)),
                ('photo', models.ImageField(editable=False, upload_to=core.models.image_file_path)),
                ('text', models.TextField(blank=True, max_length=500)),
                ('location', models.CharField(blank=True, max_length=30)),
                ('posted_on', models.DateTimeField(auto_now_add=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_posts', to=settings.AUTH_USER_MODEL)),
                ('likes', models.ManyToManyField(blank=True, related_name='likers', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'post',
                'ordering': ['-posted_on'],
            },
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('idtransaction', models.AutoField(db_column='idTransaction', primary_key=True, serialize=False)),
                ('transactionamount', models.FloatField(blank=True, db_column='TransactionAmount', null=True)),
                ('transactionresult', models.CharField(blank=True, db_column='TransactionResult', max_length=45, null=True)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='post_transaction', to='core.post')),
                ('user_idbuyer', models.ForeignKey(db_column='user_idBuyer', on_delete=django.db.models.deletion.DO_NOTHING, related_name='buyer', to=settings.AUTH_USER_MODEL)),
                ('user_idseller', models.ForeignKey(db_column='user_idSeller', on_delete=django.db.models.deletion.DO_NOTHING, related_name='seller', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'transaction',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('idcomment', models.AutoField(db_column='idComment', primary_key=True, serialize=False)),
                ('text', models.CharField(max_length=100)),
                ('posted_on', models.DateTimeField(auto_now_add=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_comments', to=settings.AUTH_USER_MODEL)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='post_comments', to='core.post')),
            ],
            options={
                'db_table': 'comment',
                'ordering': ['-posted_on'],
            },
        ),
        migrations.AddField(
            model_name='user',
            name='hobbies',
            field=models.ManyToManyField(related_name='user_hobbies', to='core.Hobby'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
    ]
