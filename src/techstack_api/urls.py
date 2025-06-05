from debug_toolbar.toolbar import debug_toolbar_urls
from django.urls import include, path
from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

import apps.core.views as core_views
import apps.posts.views as posts_views
import apps.profiles.views as profiles_views


class RootRouter(routers.DefaultRouter):
    root_viewsets = [
        profiles_views.ProfileViewSet,
        posts_views.TagViewSet,
        posts_views.PostViewSet,
        posts_views.CommentViewSet,
        posts_views.ReactionViewSet,
    ]

    def get_api_root_view(self, api_urls=None):
        api_root_dict = {}
        list_name = self.routes[0].name

        for prefix, viewset, basename in self.registry:
            if viewset in self.root_viewsets:
                api_root_dict[prefix] = list_name.format(basename=basename)

        return self.APIRootView.as_view(api_root_dict=api_root_dict)


root_router = RootRouter()
root_router.register(r"profiles", profiles_views.ProfileViewSet)
root_router.register(r"tags", posts_views.TagViewSet)
root_router.register(r"posts", posts_views.PostViewSet)
root_router.register(r"comments", posts_views.CommentViewSet)
root_router.register(r"reactions", posts_views.ReactionViewSet)
root_router.register(r"users", core_views.UserViewSet)
root_router.register(r"groups", core_views.GroupViewSet)

urlpatterns = [
    path("api/v1/", include(root_router.urls)),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/", include("rest_framework.urls", namespace="rest_framework")),
] + debug_toolbar_urls()
