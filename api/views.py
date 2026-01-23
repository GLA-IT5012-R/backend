from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


@api_view(["GET"])
def hello(request):
    return Response({"message": "Hello from Django"})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def testAuth(request):
    return Response({"message": f"Hello {request.user.username}"})
