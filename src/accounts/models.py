from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.urls import reverse_lazy
# Create your models here.

#Model Manager class that contains all the username.
class UserProfileManager(models.Manager):
    use_for_related_fields = True

    def all(self):
        qs = self.get_queryset().all()
        try:
            if self.instance:
                qs = qs.exclude(user=self.instance)
        except:
            pass
        return qs

# to check whether the user is following other users and to toggle(follow/unfollow) between the users (i.e follow or unfollow users)
    def toggle_follow(self, user, to_toggle_user):
        user_profile, created = UserProfile.objects.get_or_create(user=user) # returns either user_obj or true)
        if to_toggle_user in user_profile.following.all(): #already following the user
            user_profile.following.remove(to_toggle_user) #unfollow the user
            added = False
        else:
            user_profile.following.add(to_toggle_user) #follow the user
            added = True
        return added

# returns true if user is followed by another user-profile else return false
    def is_following(self, user, followed_by_user):
        user_profile, created = UserProfile.objects.get_or_create(user=user)
        if created:
            return False
        if followed_by_user in user_profile.following.all():
            return True
        return False

# retrun recommended list of usrnames to follow which are following logeed in user (Me)
    def recommended(self, user, limit_to=10):
        print(user)
        profile = user.profile 
        following = profile.following.all()
        following = profile.get_following()
        qs = self.get_queryset().exclude(user__in=following).exclude(id=profile.id).order_by("?")[:limit_to]
        return qs
        
	    
class UserProfile(models.Model):
    user        = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='profile') # user.profile 
    following   = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='followed_by') 
    # user.profile.following -- users I follow
    # user.followed_by -- users that follow me -- reverse relationship

    objects = UserProfileManager() # UserProfile.objects.all() 
    # abc = UserProfileManager() # UserProfile.abc.all()

    def __str__(self):
    	return str(self.following.all().count())

	# returns the usernames of following users excluding itself's username. 
    def get_following(self):
        users  = self.following.all() # User.objects.all().exclude(username=self.user.username)
        return users.exclude(username=self.user.username)

    def get_follow_url(self):
    	return reverse_lazy("profiles:follow", kwargs={"username":self.user.username}) # to reverse the url call

    def get_absolute_url(self):
    	return reverse_lazy("profiles:detail", kwargs={"username":self.user.username}) # detail view url for the logeed in user


#signal function to parse and recieve user profiles
def post_save_user_receiver(sender, instance, created, *args, **kwargs):
    if created:
        new_profile = UserProfile.objects.get_or_create(user=instance)
        # celery + redis
        # deferred task

post_save.connect(post_save_user_receiver, sender=settings.AUTH_USER_MODEL) #connecting post_save_user_receiver() method with post_save() signal
