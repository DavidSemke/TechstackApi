"""
URL configuration for techstack_api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import include, path
from rest_framework import routers

import apps.posts.views as posts_views
import apps.profiles.views as profiles_views

default_router = routers.DefaultRouter()
default_router.register(r"profiles", profiles_views.ProfileViewSet)
(default_router.register(r"posts", posts_views.PostViewSet),)
default_router.register(r"tags", posts_views.TagViewSet)
default_router.register(r"comments", posts_views.CommentViewSet)
default_router.register(r"reactions", posts_views.ReactionViewSet)

urlpatterns = [
    path("", include(default_router.urls)),
    path("", include("apps.core.urls")),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
]
