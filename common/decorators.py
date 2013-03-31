from django.http import HttpResponseBadRequest
from django.contrib.auth.decorators import login_required as _login_required
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.conf import settings

def ajax_required(f):
    """
    http://djangosnippets.org/snippets/771/
    AJAX request required decorator
    use it in your views:

    @ajax_required
    def my_view(request):
        ....

    """    
    def wrap(request, *args, **kwargs):
            if not request.is_ajax():
                return HttpResponseBadRequest()
            return f(request, *args, **kwargs)
    wrap.__doc__=f.__doc__
    wrap.__name__=f.__name__
    return wrap

class ClassProperty(property):
    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()
