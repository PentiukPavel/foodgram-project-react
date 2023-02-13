from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()

router.register(r'tags', views.TagViewSet, basename='tags')
router.register(r'ingredients',
                views.IngredientsViewSet,
                basename='ingredients')

urlpatterns = [
    path('', include(router.urls))
]
