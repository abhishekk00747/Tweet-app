import re
from django.db import models
from django.urls import reverse
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.utils import timezone

from hashtags.signals import parsed_hashtags
from .validators import validate_content
# Create your models here.



#model manager
class TweetManager(models.Manager):
    def retweet(self, user, parent_obj): #original object coming from Tweet model
    	#checking if the retweet has an original tweet and assigning it as a parent tweet
        if parent_obj.parent:   #checking if parent_obj has a existing parent (i.e original tweet)
            og_parent = parent_obj.parent  #get the original tweet and assign as og_parent
        else:
            og_parent = parent_obj #else assign same tweet to og_parent
        
        qs = self.get_queryset().filter(user=user, parent=og_parent).filter(
                    timestamp__year=timezone.now().year,
                    timestamp__month=timezone.now().month,
                    timestamp__day=timezone.now().day,
                    reply=False,
                    )
        if qs.exists():
            return None

        obj = self.model(
                parent = parent_obj,
                user = user,
                content = parent_obj.content,
            )
        obj.save()
        return obj

    def like_toggle(self, user, tweet_obj):
        if user in tweet_obj.liked.all():
            is_liked = False
            tweet_obj.liked.remove(user)
        else:
            is_liked = True
            tweet_obj.liked.add(user)
            return is_liked

#Main model
class Tweet(models.Model):
    parent      = models.ForeignKey("self", blank=True, null=True)
    user		= models.ForeignKey(settings.AUTH_USER_MODEL)
    content 	= models.CharField(max_length=140, validators=[validate_content])
    liked       = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='liked')
    reply       = models.BooleanField(verbose_name='Is a reply?', default=False)
    updated		= models.DateTimeField(auto_now=True)
    timestamp	= models.DateTimeField(auto_now_add=True)
	
    objects = TweetManager() #instance varible of TweetManager

    def __str__(self):
        return str(self.content)

    def get_absolute_url(self):
        return reverse("tweet:detail", kwargs={"pk":self.pk})

    class Meta:
        ordering = ['-timestamp'] 

    def get_parent(self):
        the_parent = self
        if self.parent:
            the_parent = self.parent
        return the_parent

    def get_children(self):
        parent = self.get_parent()
        qs = Tweet.objects.filter(parent=parent)
        qs_parent = Tweet.objects.filter(pk=parent.pk)
        return (qs | qs_parent)
        




#signal function for parsing and recieving hashtags and usernames using python regular expression
def tweet_save_receiver(sender, instance, created, *args, **kwargs):
    if created and not instance.parent:    #if tweet is created and has no parent tweet
        # notify a user
        user_regex = r'@(?P<username>[\w.@+-]+)' #python regular expression function for usernames
        usernames = re.findall(user_regex, instance.content) #findall() matches all the strings in a tweet and returns username as a list of string
        # send notification to user here.

        # send hashtag signal to user here.
        hash_regex = r'#(?P<hashtag>[\w\d-]+)' #python regular expression function for hashtags
        hashtags = re.findall(hash_regex, instance.content)  #findall() matches all the strings in a tweet and return hashtag as a list of string
        parsed_hashtags.send(sender=instance.__class__, hashtag_list=hashtags)



post_save.connect(tweet_save_receiver, sender=Tweet) #connecting tweet_save_receiver() method with post_save() signal




"""def clean(self, *args, **kwargs):
        content = self.content
        if content == "abc":
            raise ValidationError("Content cannot be ABC")
        return super(Tweet, self).clean(*args, **kwargs)"""


