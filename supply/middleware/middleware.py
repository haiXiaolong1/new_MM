
from django.shortcuts import redirect
from django.utils.deprecation import  MiddlewareMixin

class AuthMW(MiddlewareMixin):
    # 通过自定义中间件进行登录认证

    def process_request(self,request):
        if request.path_info == "/login/":
            return

        if not request.session.get("info"):
            return redirect('/login/')

        return