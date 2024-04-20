from django.db import models
from django.utils import timezone
from user import models as user_models
# Create your models here.
class Device(models.Model):
    custom_fingerprint = models.CharField(max_length=255,unique=True)
    def __str__(self):
        return f'{self.custom_fingerprint}'
class WebBrowser(models.Model):
    custom_fingerprint = models.CharField(max_length=255, unique=True)
    def __str__(self):
        return f'{self.custom_fingerprint}'
class IPObject(models.Model):
    ip_address = models.CharField(max_length=255)
    unreg_users = models.ManyToManyField(to='unreg_user.PublicUser', blank=True)
    def __str__(self):
        return f'{self.ip_address}'
class PublicUser(models.Model):
    web_browser = models.ForeignKey(WebBrowser,on_delete=models.CASCADE)
    device = models.ForeignKey(Device,null=True,blank=True,on_delete=models.CASCADE)
    ip_objects = models.ManyToManyField(IPObject,blank=True)
    def __str__(self):
        return f'{self.web_browser}'
class ReadingList(models.Model):
    public_user = models.ForeignKey(PublicUser, on_delete=models.CASCADE, null=True, blank=True)
    remain = models.PositiveIntegerField(default=2)
    read_articles = models.ManyToManyField(to='article.Article', blank=True)
    current_month_access = models.PositiveIntegerField(default=0)

    def to_dict(self):
        readlist = self
        return {
            'public_user':readlist.public_user.id,
            'remain':readlist.remain,
            'read_articles': [
                {
                    'article_id':article.article_id,
                    'title': article.title,
                    'author': article.author,
                    'image': article.image.name,
                    'author_user_id': user_models.Profile.objects.filter(base_user=article.author_user.base_user).first().user_id_profile,
                    'author_img': user_models.Profile.objects.filter(base_user=article.author_user.base_user).first().image.name,
                    'author_user_name': user_models.Profile.objects.filter(base_user=article.author_user.base_user).first().first_name + ' ' + user_models.Profile.objects.filter(base_user=article.author_user.base_user).first().last_name,
                    'published_on': article.published_on,
                    'content': article.content[:800],
                    'likes': article.likes,
                    'comment_list': [comment.id for comment in article.comment_list.all()],
                }
                for article in readlist.read_articles.all()
            ],
        }
    



