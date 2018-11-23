from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import NotAuthenticated
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from members.backends import get_user_by_access_token
from .serializers import AuthTokenSerializer, UserSerializer

User = get_user_model()


class AuthTokenView(APIView):
    """
    username, password를 받아서
    사용자 인증에 성공하면 해당 사용자와 연결된 토큰 정보와 사용자 정보를 동시에 리턴
    """

    def post(self, request):
        serializer = AuthTokenSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FacebookAuthTokenView(APIView):
    # URL: /api/members/facebook-auth-token/
    def post(self, request):
        # 전달받은 토큰(페이스북 access_token)값과
        #        유저ID(access_token, user_id)를 사용해서
        # 정상적인 token인지 검사 후
        #  (access_token으로 받아온 정보의 id와 user_id가 같은지)
        # DB에 해당 유저가 존재하는지 검사(authenticate)
        #  있다면 -> 토큰 발급
        #  없다면 -> 유저 생성 후 토큰 발급
        #           -> 생성로직은 FacebookBackend참조

        # serializer = FacebookAuthTokenSerializer(data=request.data)
        # if serializer.is_valid():
        #     return Response(serializer.data)
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # 1. 아래 코드들을 Serializer로 처리
        # 2. Serializer내부로 들어갈 아래 코드의 내용을 ClientFacebookBackend의 authenticate를 이용해서 처리
        # 3. status가 'connected'가 아닌 경우, 사용자가 추가로 페이스북 로그인 및 앱 권한 승인 후 아래 로직을 진행할 수 있도록
        #    클라이언트 코드 수정해보기
        #    FB.login() <- 이 메서드 활용할 것
        facebook_user_id = request.data.get('user_id')
        access_token = request.data.get('access_token')
        if User.objects.filter(username=facebook_user_id).exists():
            user = User.objects.get(username=facebook_user_id)
        else:
            user = get_user_by_access_token(access_token)
        token = Token.objects.get_or_create(user=user)[0]
        data = {
            'token': token.key,
            'user': UserSerializer(user).data,
        }
        return Response(data)


class UserDetailAPIView(APIView):
    # URL1: /apis/members/view/<int:pk>/
    # URL2: /apis/members/view/profile/
    def get(self, request, pk=None):
        if pk:
            user = get_object_or_404(User, pk=pk)
        else:
            user = request.user
            if not user.is_authenticated:
                raise NotAuthenticated()
        serializer = UserSerializer(user)
        return Response(serializer.data)


class UserDetail(generics.RetrieveAPIView):
    # URL1: /apis/members/<int:pk>/
    # URL2: /apis/members/profile/
    #  2개의 URL에 모두 매칭되도록

    # generics.GenericAPIView를 참고해서
    #  get_object() 메서드를 적절히 오버라이드
    #   pk값이 주어지면 pk에 해당하는 User를 리턴 (기본값)
    #   pk값이 주어지지 않았다면 request.user에 해당하는 User를 리턴
    #   pk값이 주어지지 않았는데 request.user가 인증되지 않았다면 예외 일으키기

    # 돌려주는 데이터는 유저정보 serialize결과
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_object(self):
        # 하나의 Object를 특정화 하기 위한 조건을 가진 필드명 또는 URL패턴명
        #  기본값: 'pk'
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        # 'pk'가 URL패턴명중에 없으면
        if lookup_url_kwarg not in self.kwargs:
            # 근데 인증된 상태도 아니라면
            if not self.request.user.is_authenticated:
                raise NotAuthenticated()
            return self.request.user

        # 'pk'가 URL패턴명에 있으면,
        # 기존 GenericAPIView에서의 동작을 그대로 실행
        return super().get_object()
