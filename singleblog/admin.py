from django.contrib import admin
from models import Blog, Author, Comment, Category, Tag

class BlogAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'published_date', 'updated_date', 'content','count']


class AuthorAdmin(admin.ModelAdmin):
    list_display = ['user_name', 'email', 'password', 'level', 'description', 'is_active']


class CommentAdmin(admin.ModelAdmin):
    list_display = ['sender', 'receiver_id', 'blog', 'add_time', 'content']

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['category_name', 'author']

class TagAdmin(admin.ModelAdmin):
    list_display = ['tag_name', 'author']

admin.site.register(Blog, BlogAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)

