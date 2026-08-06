from django.contrib import admin

from .models import (
    Country,
    Level,
    Profile,
    Question,
    Reply,
    SavedScholarship,
    Scholarship,
    SuccessStory,
)


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ("label", "code", "order")
    ordering = ("order", "label")


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ("name", "code")
    search_fields = ("name", "code")


@admin.register(Scholarship)
class ScholarshipAdmin(admin.ModelAdmin):
    list_display = ("title", "university", "level_list", "funding_type", "deadline", "is_active")
    list_editable = ("is_active",)          # tick/untick right from the list page -- this IS your publish switch
    list_filter = ("levels", "funding_type", "nationality_scope", "is_active")
    search_fields = ("title", "university", "description")
    prepopulated_fields = {"slug": ("title",)}   # optional -- auto-fills the slug as you type the title
    filter_horizontal = ("eligible_countries", "levels")  # nicer widget than a giant multi-select box
    date_hierarchy = "deadline"

    def level_list(self, obj):
        return ", ".join(level.label for level in obj.levels.all())
    level_list.short_description = "Levels"


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "country")
    search_fields = ("user__username", "user__email")


@admin.register(SavedScholarship)
class SavedScholarshipAdmin(admin.ModelAdmin):
    list_display = ("user", "scholarship", "status", "saved_at")
    list_filter = ("status",)


@admin.register(SuccessStory)
class SuccessStoryAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "is_published", "created_at")
    list_editable = ("is_published",)
    list_filter = ("is_published",)
    search_fields = ("title", "story", "author__username")


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "scholarship", "created_at")
    search_fields = ("title", "body", "author__username")


@admin.register(Reply)
class ReplyAdmin(admin.ModelAdmin):
    list_display = ("question", "author", "created_at")
    search_fields = ("body", "author__username")

"""
ADD THESE to admin.py
"""

from django.contrib import admin

from .models import Notification, StoryComment


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["user", "message", "is_read", "created_at"]
    list_filter = ["is_read"]
    search_fields = ["user__username", "message"]


@admin.register(StoryComment)
class StoryCommentAdmin(admin.ModelAdmin):
    list_display = ["story", "author", "created_at"]
    search_fields = ["body", "author__username"]