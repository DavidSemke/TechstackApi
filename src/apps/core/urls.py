from rest_framework import routers

from .views import GroupViewSet, UserViewSet

router = routers.SimpleRouter()
router.register(r"users", UserViewSet)
router.register(r"groups", GroupViewSet)

# Non-default paths only
urlpatterns = router.urls
