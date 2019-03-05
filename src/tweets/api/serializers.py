from rest_framework import serializers
from django.utils.timesince import timesince


from accounts.api.serializers import UserDisplaySerializer
from tweets.models import Tweet

"""Serializers allow complex data such as querysets and model instances to be 
converted to native Python datatypes that can then be easily rendered into JSON, XML or other content types."""


class ParentTweetModelSerializer(serializers.ModelSerializer):
	user = UserDisplaySerializer(read_only=True) #write_only
	date_display = serializers.SerializerMethodField()
	timesince = serializers.SerializerMethodField()
	likes = serializers.SerializerMethodField()
	did_like = serializers.SerializerMethodField()
	
	class Meta:
		model = Tweet
		fields = ['id', 'user', 'content', 'timestamp', 'date_display', 'timesince', 'likes','did_like',]

	def get_did_like(self, obj):
		request = self.context.get("request")
		try:
			user = request.user
			if user.is_authenticated():
				if user in obj.liked.all():
					return True
		except:
			pass
		return False


	def get_likes(self, obj):
		return obj.liked.all().count()


	def get_date_display(self, obj):
		return obj.timestamp.strftime("%b %d, %Y at %I:%M %p")


	def get_timesince(self, obj):
		return timesince(obj.timestamp) + " ago"


#Main model serielizers
class TweetModelSerializer(serializers.ModelSerializer):
	parent_id = serializers.CharField(write_only=True, required=False)
	user = UserDisplaySerializer(read_only=True) #write_only
	date_display = serializers.SerializerMethodField()
	timesince = serializers.SerializerMethodField()
	parent = ParentTweetModelSerializer(read_only=True) #get the parent tweet and display in retweet
	likes = serializers.SerializerMethodField()
	did_like = serializers.SerializerMethodField()

	class Meta:
		model = Tweet
		fields = ['parent_id', 'id', 'user', 'content', 'timestamp', 'date_display', 'timesince', 'parent', 'likes', 'did_like', 'reply',]

		#read_only_fields = ['reply']

	#check whether the user has already liked it and return true or false.
	def get_did_like(self, obj):
		request = self.context.get("request")
		try:
			user = request.user
			if user.is_authenticated():
				if user in obj.liked.all():  #if user object is already there in the liked queryset
					return True
		except:
			pass
		return False


	def get_likes(self, obj):
		return obj.liked.all().count()


	def get_date_display(self, obj):
		return obj.timestamp.strftime("%b %d, %Y at %I:%M %p")


	def get_timesince(self, obj):
		return timesince(obj.timestamp) + " ago"