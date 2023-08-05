"""
Views for the uesr API.
"""
from rest_framework import generics

from user.serializer import UserSerializer


class CreateUserView(generics.CreateAPIView):
    """Create  a new user in the system."""
    serializer_class = UserSerializer


