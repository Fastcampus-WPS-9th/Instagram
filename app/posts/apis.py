import json

from django.http import HttpResponse
from rest_framework import permissions, generics

from .models import HashTag, Post
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


class PostLikeCreate:
    pass


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
