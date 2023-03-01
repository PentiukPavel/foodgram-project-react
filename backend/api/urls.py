from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()

router.register(r'tags', views.TagViewSet, basename='tags')
router.register(r'ingredients',
                views.IngredientsViewSet,
                basename='ingredients')
router.register(r'recipes', views.RecipeViewSet, basename='recipes')
router.register(r'users/subscriptions',
                views.SubscriptionView,
                basename='subscriptions')
router.register(r'users',
                views.CustomUserView,
                basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
