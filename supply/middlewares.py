import time
from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import HttpResponse,render
# 访问IP池
visit_ip_pool = {}
class IPmiddleware(MiddlewareMixin):
    def process_request(self,request):
        # 获取访问者IP
        ip=request.META.get("REMOTE_ADDR")
        # 获取访问当前时间
        visit_time=time.time()
        # 判断如果访问IP不在池中,就将访问的ip时间插入到对应ip的key值列表,如{"127.0.0.1":[时间1]}
        if ip not in visit_ip_pool:
            visit_ip_pool[ip]=[visit_time]
            return None
        # 然后在从池中取出时间列表
        history_time = visit_ip_pool.get(ip)
        # 循环判断当前ip的时间列表，有值，并且当前时间减去列表的最后一个时间大于60s，把这种数据pop掉，这样列表中只有60s以内的访问时间，
        while history_time and visit_time-history_time[-1]>3:
            history_time.pop()
        # 如果访问次数小于10次就将访问的ip时间插入到对应ip的key值列表的第一位置,如{"127.0.0.1":[时间2,时间1]}
        print(history_time)
        if len(history_time)<10:
            history_time.insert(0, visit_time)
            return None
        else:
            # 如果大于10次就禁止访问
            return render(request, '418teapot.html')

