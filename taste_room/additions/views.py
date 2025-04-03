from django.shortcuts import render
from django.views.generic import TemplateView

class Error404View(TemplateView):
    template_name = "additions/error_404.html"


class ErrorModeratorView(TemplateView):
    template_name = "additions/error_moderator.html"
