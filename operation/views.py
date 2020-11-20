from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from register.views import User, OnlyYouMixin

class Top(OnlyYouMixin, generic.DetailView):
    template_name = 'operation/top.html'
    model = User
    login_url = '/'

class Api(generic.TemplateView):
    template_name = 'operation/api.html'