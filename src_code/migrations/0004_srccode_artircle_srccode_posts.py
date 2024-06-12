# Generated by Django 4.2.7 on 2024-06-05 02:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('article', '0006_remove_article_src_code'),
        ('post', '0008_remove_post_src_code'),
        ('src_code', '0003_alter_srccode_content'),
    ]

    operations = [
        migrations.AddField(
            model_name='srccode',
            name='artircle',
            field=models.ManyToManyField(blank=True, related_name='src_code_article', to='article.article'),
        ),
        migrations.AddField(
            model_name='srccode',
            name='posts',
            field=models.ManyToManyField(blank=True, related_name='src_code_post', to='post.post'),
        ),
    ]