from django.http import HttpResponseServerError
from django.shortcuts import render

def my_customized_server_error(request, template_name='500.html'):
    import sys
    from django.views import debug
    error_html = debug.technical_500_response(request, *sys.exc_info()).content
    return HttpResponseServerError(error_html)

def request(request):
    return render(request,'request.html')