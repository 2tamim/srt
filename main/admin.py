from django.contrib import admin
from .models import ProjectCategory, ProjectArea, Product, AccessType, PrivilegeLevel, UserExtension, ProductCategory


# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)


admin.site.register(ProjectCategory, CategoryAdmin)


class ProjectAreaAdmin(admin.ModelAdmin):
    list_display = ('name',)


admin.site.register(ProjectArea, ProjectAreaAdmin)


class UserExtensionAdmin(admin.ModelAdmin):
    list_display = ('user', 'access', 'avatar',)


admin.site.register(UserExtension, UserExtensionAdmin)


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name',)


admin.site.register(Product, ProductAdmin)


class AccessTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)


admin.site.register(AccessType, AccessTypeAdmin)


class PrivilegeLevelAdmin(admin.ModelAdmin):
    list_display = ('name','admin',)


admin.site.register(PrivilegeLevel, PrivilegeLevelAdmin)


class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)


admin.site.register(ProductCategory, ProductCategoryAdmin)



