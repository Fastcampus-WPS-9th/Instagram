from rest_framework import serializers

from .models import Post, PostLike


class PostSerializer(serializers.ModelSerializer):
    # 작성자
    # 댓글목록
    # 좋아요 누른 사람 목록
    class Meta:
        model = Post
        fields = (
            'pk',
            'author',
            'photo',
            'created_at',
        )
        read_only_fields = (
            'author',
        )


class PostLikeSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        model = PostLike
        fields = (
            'post',
            'user',
        )
        read_only_fields = (
            'user',
        )
