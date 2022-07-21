
from django.shortcuts import redirect
from django.utils.deprecation import  MiddlewareMixin

class AuthMW(MiddlewareMixin):


    def process_request(self,request):
        print(1)
        if request.path_info == "/login/":
            return

        if not request.session.get("info"):
            return redirect('/login/')

        return