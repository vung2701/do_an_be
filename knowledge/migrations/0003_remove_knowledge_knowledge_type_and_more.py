# Generated by Django 4.2.7 on 2024-05-18 15:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('knowledge', '0002_knowledge_created_on_knowledge_modified_on'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='knowledge',
            name='knowledge_type',
        ),
        migrations.AddField(
            model_name='knowledge',
            name='knowledge_types',
            field=models.ManyToManyField(related_name='knowledges', to='knowledge.knowledgetype'),
        ),
    ]
