from django.http import JsonResponse
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import render


def home(request: HttpRequest) -> HttpResponse:
    return render(request, 'index.html')


def health(request: HttpRequest) -> JsonResponse:
    return JsonResponse({'status': 'ok'})
