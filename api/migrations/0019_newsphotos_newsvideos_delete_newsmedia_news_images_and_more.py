# Generated by Django 4.2.6 on 2023-12-08 13:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0018_remove_news_image_newsmedia'),
    ]

    operations = [
        migrations.CreateModel(
            name='NewsPhotos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(default='news_photos/news_photo.jpg', upload_to='news_photos/', verbose_name='Фото к новости')),
            ],
        ),
        migrations.CreateModel(
            name='NewsVideos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('video', models.FileField(default='news_photos/news_photo.jpg', upload_to='news_videos', verbose_name='Видео к новости')),
            ],
        ),
        migrations.DeleteModel(
            name='NewsMedia',
        ),
        migrations.AddField(
            model_name='news',
            name='images',
            field=models.ManyToManyField(to='api.newsphotos', verbose_name='Фото к новости'),
        ),
        migrations.AddField(
            model_name='news',
            name='videos',
            field=models.ManyToManyField(to='api.newsvideos', verbose_name='Видео к новости'),
        ),
    ]
