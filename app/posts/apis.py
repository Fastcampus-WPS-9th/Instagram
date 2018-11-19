import json

from django.http import HttpResponse
from rest_framework import permissions, generics, status
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import HashTag, Post, PostLike
from .serializers import PostSerializer


# generics.ListCreateAPIView
class PostList(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
    )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PostDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
    )


class PostLikeCreate(APIView):
    permission_classes = (
        permissions.IsAuthenticated,
    )

    def post(self, request, post_pk):
        # URL1: /posts/like/
        # URL2: /posts/<post_pk>/like/
        # 특정 Post에 대해서 request.user의
        # PostLike를 만든다
        #  조건: request.user와 해당 Post에 연결된 PostLike가 없어야 함
        post = get_object_or_404(Post, pk=post_pk)
        # 위 user, post와 연결된 PostLike가 있는지
        if PostLike.objects.filter(user=request.user, post=post).exists():
            data = {
                'detail': '이미 좋아요를 누른 포스트입니다',
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        post_like = PostLike.objects.create(user=request.user, post=post)
        return Response(status=status.HTTP_201_CREATED)


class PostLikeDelete:
    pass


def tag_search(request):
    # URL: '/posts/api/tag-search/'

    # request.GET으로 전달된
    #  keyword값을 가지는(contains)

    #  HashTag목록을 가져와 각 항목을 dict로 변경
    #   dict요소의 list로 만들어 HttpResponse에 리턴
    #  ex) [{}, {}, {}]
    keyword = request.GET.get('keyword')
    tags = []
    if keyword:
        tags = list(HashTag.objects.filter(name__istartswith=keyword).values())
    result = json.dumps(tags)
    return HttpResponse(result, content_type='application/json')
