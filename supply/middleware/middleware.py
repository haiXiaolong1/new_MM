
from django.shortcuts import redirect
from django.utils.deprecation import  MiddlewareMixin

class AuthMW(MiddlewareMixin):
    # 通过自定义中间件进行登录认证

    def process_request(self,request):
        if request.path_info == "/login/" or request.path_info == "/account/ac/password/" or \
                request.path_info == "/account/ac/send/" or request.path_info == "/account/ac/login/"\
                or request.path_info =="/forgot" or request.path_info == "/supply/r_password":
            return

        if not request.session.get("info"):
            return redirect('/login/')

        return