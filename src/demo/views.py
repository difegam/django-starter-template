from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import render


# Remove
def home(request: HttpRequest) -> HttpResponse:
    return render(request, 'index.html')
