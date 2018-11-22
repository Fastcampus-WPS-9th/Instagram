from rest_framework import serializers

from members.serializers import UserSerializer
from .models import Post, PostLike, Comment


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer()

    class Meta:
        model = Comment
        fields = (
            'pk',
            'author',
            'content',
        )


class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer()
    is_like = serializers.SerializerMethodField()
    comments = CommentSerializer(many=True)

    class Meta:
        model = Post
        fields = (
            'pk',
            'author',
            'photo',
            'created_at',
            'is_like',
            'comments',
        )
        read_only_fields = (
            'author',
        )

    def get_is_like(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            try:
                postlike = obj.postlike_set.get(user=user)
                return PostLikeSerializer(postlike).data
            except PostLike.DoesNotExist:
                return


class PostLikeSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        model = PostLike
        fields = (
            'pk',
            'post',
            'user',
            'created_at',
        )
        read_only_fields = (
            'user',
        )
