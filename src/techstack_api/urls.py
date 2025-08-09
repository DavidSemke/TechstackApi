from debug_toolbar.toolbar import debug_toolbar_urls
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers

import apps.core.views as core_views
import apps.posts.views as posts_views
import apps.profiles.views as profiles_views

root_router = routers.DefaultRouter()
root_router.register(r"profiles", profiles_views.ProfileViewSet)
root_router.register(r"tags", posts_views.TagViewSet)
root_router.register(r"posts", posts_views.PostViewSet)
root_router.register(r"comments", posts_views.CommentViewSet)
root_router.register(r"reactions", posts_views.ReactionViewSet)

auth_router = routers.DefaultRouter()
auth_router.register(r"users", core_views.UserViewSet)
auth_router.register(r"groups", core_views.GroupViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/", include("rest_framework.urls", namespace="rest_framework")),
    path("api/v1/", include(root_router.urls)),
    path("api/auth/", include(auth_router.urls)),
    path("api/auth/", include("djoser.urls.jwt")),
    path("silk/", include("silk.urls", namespace="silk")),
] + debug_toolbar_urls()
