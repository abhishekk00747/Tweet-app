from rest_framework import generics
from django.db.models import Q
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response


from tweets.models import Tweet

from .pagination import StandardResultsPagination
from .serializers import TweetModelSerializer


#saving the like toggle button
class LikeToggleAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated] # to make sure user is authenticated
    def get(self, request, pk, format=None):
        tweet_qs = Tweet.objects.filter(pk=pk)
        message = "Not allowed"
        if request.user.is_authenticated():
            is_liked = Tweet.objects.like_toggle(request.user, tweet_qs.first())
            return Response({'liked': is_liked})
        return Response({"message": message}, status=400)



#retweet view after user do a retweet of an existing tweet
class RetweetAPIView(APIView):
	permission_classes = [permissions.IsAuthenticated] # to make sure user is authenticated

	def get(self, request, pk, format=None):
		tweet_qs = Tweet.objects.filter(pk=pk)
		message = "Not allowed"
		if tweet_qs.exists() and tweet_qs.count() == 1:
			if request.user.is_authenticated():
				new_tweet = Tweet.objects.retweet(request.user, tweet_qs.first()) #retweeting the orignal tweet
				if new_tweet is not None:
					data = TweetModelSerializer(new_tweet).data # retweet data
					return Response(data)
				message = "Cannot retweet the same in 1 day"

		return Response({"message": message}, status=400)



class TweetCreateAPIView(generics.CreateAPIView):
    serializer_class = TweetModelSerializer
    permission_classes = [permissions.IsAuthenticated] # to make sure user is authenticated

    def perform_create(self, serializer):
    	serializer.save(user=self.request.user)


class TweetDetailAPIView(generics.ListAPIView):
    queryset = Tweet.objects.all()
    serializer_class = TweetModelSerializer
    pagination_class = StandardResultsPagination
    permission_classes = [permissions.AllowAny]

    def get_queryset(self, *args, **kwargs):
        tweet_id = self.kwargs.get("pk")
        qs = Tweet.objects.filter(pk=tweet_id)
        if qs.exists() and qs.count() == 1:
            parent_obj = qs.first()
            qs1 = parent_obj.get_children()
            qs = (qs | qs1).distinct().extra(select={"parent_id_null": 'parent_id IS NULL'})
        return qs.order_by("-parent_id_null", '-timestamp')
        
class SearchTweetAPIView(generics.ListAPIView):
    queryset = Tweet.objects.all().order_by("-timestamp")
    serializer_class = TweetModelSerializer
    pagination_class = StandardResultsPagination

    def get_serializer_context(self, *args, **kwargs):
        context = super(SearchTweetAPIView, self).get_serializer_context(*args, **kwargs)
        context['request'] = self.request
        return context

    def get_queryset(self, *args, **kwargs):
        qs = self.queryset
        query = self.request.GET.get("q", None)
        if query is not None:
            qs = qs.filter(
                    Q(content__icontains=query) |
                    Q(user__username__icontains=query)
                    )
        return qs


class TweetListAPIView(generics.ListAPIView):
	serializer_class = TweetModelSerializer
	pagination_class = StandardResultsPagination

	def get_serializer_context(self, *args, **kwargs):
		context = super(TweetListAPIView, self).get_serializer_context(*args, **kwargs)
		context['request'] = self.request
		return context
	
	# this method will get the all the tweet data (queryset) of the user
	def get_queryset(self, *args, **kwargs):
	    requested_user = self.kwargs.get("username") #get username
	        
	    if requested_user:
	        qs = Tweet.objects.filter(user__username=requested_user).order_by("-timestamp") #get tweets of requested user
	    else:
	        im_following = self.request.user.profile.get_following() # get the usernames of users's I am following or return none
	        qs1 = Tweet.objects.filter(user__in=im_following) #filter the tweets of unfollowed users and get only following user's tweet
	        qs2 = Tweet.objects.filter(user=self.request.user) #get the user's own tweets
	        qs = (qs1 | qs2).distinct().order_by("-timestamp") #combine the above two queryset(q1,q2) of tweets and filter the duplicate ones and display LIFO order
	        
	    query = self.request.GET.get("q", None)
	    if query is not None:
	        qs = qs.filter(
	                Q(content__icontains=query) |
	                Q(user__username__icontains=query)
	                )
	    return qs

class SearchAPIView(generics.ListAPIView):
    serializer_class = TweetModelSerializer
    pagination_class = StandardResultsPagination

    def get_queryset(self, *args, **kwargs):
        qs = Tweet.objects.all().order_by("-timestamp")
        query = self.request.GET.get("q", None)
        if query is not None:
            qs = qs.filter(
                    Q(content__icontains=query) |
                    Q(user__username__icontains=query)
                    )
        return qs