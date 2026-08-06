"""
Scholarship app — Function-Based Views
---------------------------------------
Four views, kept intentionally simple:

1. scholarship_list      -> browse + search + filter (the homepage/listing)
2. scholarship_detail    -> a single scholarship's full page
3. toggle_save_scholarship -> the "like" button under each card (login required)
4. profile_view          -> shows the logged-in user's bio + their saved list

Nothing fancy here — no class-based views, no AJAX. Just requests in,
templates out. Once this feels comfortable, upgrading pieces (e.g. making
the like button AJAX-powered) is an easy next step.
"""

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ProfileForm, QuestionForm, ReplyForm, SignupForm, SuccessStoryForm, StoryCommentForm
from .models import (
    Country,
    FundingType,
    Level,
    Question,
    SavedScholarship,
    Scholarship,
    SuccessStory,
    Notification, 
    SuccessStory,
)




def scholarship_list(request):
    """
    The main browse page. Anyone can view this (no login required).
    Supports search (?q=) and filters (?level=, ?funding_type=, ?country=).
    """
    scholarships = Scholarship.objects.filter(is_active=True).order_by("deadline")

    # --- 1. Keyword search ---
    query = request.GET.get("q", "").strip()
    if query:
        scholarships = scholarships.filter(
            Q(title__icontains=query)
            | Q(university__icontains=query)
            | Q(description__icontains=query)
        )

    # --- 2. Filter by level (bachelors/masters/phd/...) ---
    # A scholarship can now have multiple levels, so this matches any
    # scholarship that includes the selected level among its own.
    selected_level = request.GET.get("level", "")
    if selected_level:
        scholarships = scholarships.filter(levels__id=selected_level).distinct()

    # --- 3. Filter by funding type ---
    selected_funding_type = request.GET.get("funding_type", "")
    if selected_funding_type:
        scholarships = scholarships.filter(funding_type=selected_funding_type)

    # --- 4. Filter by country ---
    # A scholarship counts as a match if it's open to everyone OR if the
    # chosen country is specifically listed as eligible.
    selected_country = request.GET.get("country", "")
    if selected_country:
        scholarships = scholarships.filter(
            Q(nationality_scope="all") | Q(eligible_countries__id=selected_country)
        ).distinct()

    # --- 5. Know which cards should show the like button as "already saved" ---
    saved_ids = set()
    if request.user.is_authenticated:
        saved_ids = set(
            SavedScholarship.objects.filter(user=request.user).values_list("scholarship_id", flat=True)
        )

    # --- 6. Pagination so the page doesn't load thousands of cards at once ---
    paginator = Paginator(scholarships, 12)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "page_obj": page_obj,
        "saved_ids": saved_ids,
        # for building the filter dropdowns in the template
        "levels": Level.objects.all(),
        "funding_types": FundingType.choices,
        "countries": Country.objects.all(),
        # so the template can keep the filters selected after submitting
        "query": query,
        "selected_level": selected_level,
        "selected_funding_type": selected_funding_type,
        "selected_country": selected_country,
    }
    return render(request, "core/scholarship_list.html", context)


def scholarship_detail(request, slug):
    """Full detail page for one scholarship. Open to everyone."""
    scholarship = get_object_or_404(Scholarship, slug=slug, is_active=True)

    is_saved = False
    if request.user.is_authenticated:
        is_saved = SavedScholarship.objects.filter(
            user=request.user, scholarship=scholarship
        ).exists()

    context = {
        "scholarship": scholarship,
        "is_saved": is_saved,
    }
    return render(request, "core/scholarship_detail.html", context)


def _is_ajax(request):
    """True if this request came from our fetch() call rather than a normal form submit."""
    return request.headers.get("X-Requested-With") == "XMLHttpRequest"


@login_required
@require_POST
def toggle_save_scholarship(request, slug):
    """
    The bookmark/"save" button under each scholarship card.

    Called via fetch() from save-button.js, so this returns JSON and the
    button animates client-side with no page reload. It still degrades
    gracefully to a normal redirect if JS is off and the surrounding
    <form> just does a regular POST.
    """
    scholarship = get_object_or_404(Scholarship, slug=slug)

    saved_entry, created = SavedScholarship.objects.get_or_create(
        user=request.user, scholarship=scholarship
    )
    if not created:
        saved_entry.delete()
        is_saved = False
        message = f"Removed '{scholarship.title}' from your saved list."
    else:
        is_saved = True
        message = f"Saved '{scholarship.title}'!"

    if _is_ajax(request):
        return JsonResponse({"is_saved": is_saved, "message": message, "slug": scholarship.slug})

    if is_saved:
        messages.success(request, message)
    else:
        messages.info(request, message)

    # Send the user back to whichever page they clicked the button from
    # (the list page, the detail page, wherever). The template will include
    # a hidden "next" field pointing at request.path.
    next_url = request.POST.get("next") or "scholarship-list"
    return redirect(next_url)


@login_required
def profile_view(request):
    """Shows the logged-in user's bio/country + everything they've saved."""
    saved_scholarships = (
        SavedScholarship.objects.filter(user=request.user)
        .select_related("scholarship")
        .order_by("-saved_at")
    )

    context = {
        "profile": request.user.profile,
        "saved_scholarships": saved_scholarships,
    }
    return render(request, "core/profile.html", context)


@login_required
def profile_edit(request):
    """Lets a user set/update their bio and country."""
    profile = request.user.profile

    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect("profile")
    else:
        form = ProfileForm(instance=profile)

    return render(request, "core/profile_edit.html", {"form": form})


def signup_view(request):
    """
    Login and logout are handled by Django's built-in auth views (wired up
    in urls.py) since they don't need any custom logic. Signup does need a
    little custom logic — creating the account, then logging the user in
    right away — so it gets its own function-based view.
    """
    if request.user.is_authenticated:
        return redirect("scholarship-list")

    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # log them in immediately, no separate login step
            messages.success(request, f"Welcome aboard, {user.username}!")
            return redirect("scholarship-list")
    else:
        form = SignupForm()

    return render(request, "registration/signup.html", {"form": form})


# ---------------------------------------------------------------------------
# Success Stories
# ---------------------------------------------------------------------------

def success_story_list(request):
    """Public board of published success stories, newest first."""
    stories = SuccessStory.objects.filter(is_published=True).select_related("author")
    paginator = Paginator(stories, 10)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "core/success_story_list.html", {"page_obj": page_obj})


def success_story_detail(request, pk):
    story = get_object_or_404(SuccessStory, pk=pk, is_published=True)
    return render(request, "core/success_story_detail.html", {"story": story})


@login_required
def success_story_create(request):
    """Post a success story. Publishes immediately -- no approval step."""
    if request.method == "POST":
        form = SuccessStoryForm(request.POST)
        if form.is_valid():
            story = form.save(commit=False)
            story.author = request.user
            story.save()
            messages.success(request, "Your story is live. Thanks for sharing!")
            return redirect("story-detail", pk=story.pk)
    else:
        form = SuccessStoryForm()

    return render(request, "core/success_story_form.html", {"form": form})


# ---------------------------------------------------------------------------
# Q&A
# ---------------------------------------------------------------------------

def question_list(request):
    """Open Q&A board -- every question, newest first."""
    questions = Question.objects.select_related("author", "scholarship").annotate(
        reply_count=Count("replies")
    )
    paginator = Paginator(questions, 15)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "core/question_list.html", {"page_obj": page_obj})


def question_detail(request, pk):
    """A single question plus its replies, with a reply box for logged-in users."""
    question = get_object_or_404(Question.objects.select_related("scholarship", "author"), pk=pk)
    replies = question.replies.select_related("author")  # type: ignore[attr-defined]

    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.info(request, "Please log in to reply.")
            return redirect("login")
        reply_form = ReplyForm(request.POST)
        if reply_form.is_valid():
            reply = reply_form.save(commit=False)
            reply.question = question
            reply.author = request.user
            reply.save()
            return redirect("question-detail", pk=question.pk)
    else:
        reply_form = ReplyForm()

    context = {
        "question": question,
        "replies": replies,
        "reply_form": reply_form,
    }
    return render(request, "core/question_detail.html", context)


@login_required
def question_create(request):
    if request.method == "POST":
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.author = request.user
            question.save()
            return redirect("question-detail", pk=question.pk)
    else:
        form = QuestionForm()

    return render(request, "core/question_form.html", {"form": form})


def success_story_detail(request, pk):
    story = get_object_or_404(SuccessStory, pk=pk, is_published=True)
    comments = story.comments.select_related("author")

    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect("login")
        comment_form = StoryCommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.story = story
            comment.author = request.user
            comment.save()
            return redirect("story-detail", pk=story.pk)
    else:
        comment_form = StoryCommentForm()

    context = {
        "story": story,
        "comments": comments,
        "comment_form": comment_form,
    }
    return render(request, "core/success_story_detail.html", context)


"""
3. ADD these two new views anywhere below your existing ones.
   These power the bell dropdown clicks.
"""


@login_required
def mark_notification_read(request, pk):
    """
    Clicking a notification in the dropdown hits this URL: it marks the
    notification read, then sends the user on to wherever it points
    (the question, the story, the scholarship). A plain GET works fine here
    since nothing destructive happens and it's user-initiated navigation.
    """
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    if not notification.is_read:
        notification.is_read = True
        notification.save(update_fields=["is_read"])
    return redirect(notification.url or "scholarship-list")


@login_required
def mark_all_notifications_read(request):
    """The "mark all as read" link/button at the bottom of the dropdown."""
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return redirect(request.POST.get("next") or "scholarship-list")