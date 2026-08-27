from rest_framework.routers import DefaultRouter

from .views import IslandTemplateViewSet, ModuleViewSet, IslandViewSet

router = DefaultRouter()
router.register("island-templates", IslandTemplateViewSet, basename="island-template")
router.register("modules", ModuleViewSet, basename="module")
router.register("islands", IslandViewSet, basename="island")

urlpatterns = router.urls