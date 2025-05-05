from django.contrib.auth.models import Group, User
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ["url", "username", "email", "groups"]


# Group ideas:
# 1 - Author (able to create/edit/delete their posts)
# 2 - Commenter (able to create/edit/delete their comments)
# 3 - Moderator (able to delete/edit content, remove Author/Commenter permissions)
class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ["url", "name"]
