from django.contrib import admin

from .models import Ingredients, RecipeIngredient, Recipes, RecipeTag, Tag

admin.site.register(Ingredients)
admin.site.register(RecipeIngredient)
admin.site.register(Recipes)
admin.site.register(RecipeTag)
admin.site.register(Tag)
