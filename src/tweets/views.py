from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView

from .forms import TweetModelForm
from .mixins import FormUserNeededMixin, UserOwnermixin
from .models import Tweet


# for retweeting existing tweet
class RetweetView(View):
    def get(self, request, pk, *args, **kwargs):
        tweet = get_object_or_404(Tweet, pk=pk)
        if request.user.is_authenticated():
            new_tweet = Tweet.objects.retweet(request.user, tweet) #retweeting the orignal tweet
            return HttpResponseRedirect("/") # go to home page
        return HttpResponseRedirect(tweet.get_absolute_url()) # go to original tweet


#Create
class TweetCreateView(FormUserNeededMixin, CreateView):
	
	form_class = TweetModelForm
	template_name = 'tweets/create_view.html'
	#success_url = reverse_lazy("tweet:detail")
    

#update
class TweetUpdateView(LoginRequiredMixin, UserOwnermixin, UpdateView):
	queryset = Tweet.objects.all()
	form_class = TweetModelForm
	template_name = 'tweets/update_view.html'
	#success_url = "/tweet/"


#Delete
class TweetDeleteView(LoginRequiredMixin, DeleteView):
	model = Tweet
	template_name = 'tweets/delete_confirm.html'
	success_url = reverse_lazy("tweet:list")  #translates to /tweet/list/
          

#Retrieve
class TweetDetailView(DetailView): # by default this view know the default template name and place (tweet_detail.html)
	queryset = Tweet.objects.all()
	
	

class TweetListView(LoginRequiredMixin, ListView): # by default this view know the default template name and place (tweet_list.html)

	def get_queryset(self, *args, **kwargs):
		qs = Tweet.objects.all()             # getting the queryset from database
		query = self.request.GET.get("q", None)
		if query is not None:
			qs = qs.filter(
				Q(content__icontains=query) | 
				Q(user__username__icontains=query)
				)
		return qs

	def get_context_data(self, *args, **kwargs):
		context = super(TweetListView, self).get_context_data(*args, **kwargs)
		context['create_form'] = TweetModelForm()
		context['create_url'] = reverse_lazy("tweet:create") #translates to /tweet/create/
		return context

		


"""def tweet_detail_view(request, id=1):
	#GET from database
	#obj = Tweet.objects.get(id=id)
	obj = get_object_or_404(Tweet, pk=pk)
	print(obj)  

	context = {
		"object": obj
	}
	return render(request, "tweets/detail_view.html", context)"""


"""def tweet_list_view(request):
	queryset = Tweet.objects.all()
	print(queryset)
	for obj in queryset:
		print(obj.content)
		
	context = {
		"object_list": queryset
	}
	return render(request, "tweets/list_view.html", context)"""

