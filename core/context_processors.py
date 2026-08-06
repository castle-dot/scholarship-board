"""
PUT THIS FILE AT:
    <your_app>/context_processors.py

THEN in settings.py, find TEMPLATES -> OPTIONS -> "context_processors" and
add this app's version to the list:

    TEMPLATES = [
        {
            ...
            "OPTIONS": {
                "context_processors": [
                    "django.template.context_processors.debug",
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                    "scholarships.context_processors.notifications",  # <-- add this line
                ],
            },
        },
    ]

Why a context processor instead of adding this to every single view? Because
the bell needs to show up in the nav bar on EVERY page (question pages,
story pages, scholarship pages...). Without this, you'd have to remember
to add "unread_count" to the context dict of every view, every time. A
context processor runs once per request and merges its result into every
template automatically.
"""


def notifications(request):
    if not request.user.is_authenticated:
        return {}

    all_notifications = request.user.notifications.order_by("-created_at")

    return {
        "unread_notifications": all_notifications[:5],   # shown in the dropdown
        "unread_count": all_notifications.filter(is_read=False).count(),
    }