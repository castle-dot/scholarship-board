from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

class FundingType(models.TextChoices):
    FULLY_FUNDED = "fully_funded", "Fully Funded"
    PARTIALLY_FUNDED = "partially_funded", "Partially Funded"
    SELF_FUNDED = "self_funded", "Self Funded / Tuition Waiver Only"


class NationalityScope(models.TextChoices):
    ALL = "all", "Open to All Nationalities"
    SPECIFIC = "specific", "Specific Countries Only"


class Level(models.Model):
    """
    A single education level (Bachelor's, Master's, PhD, ...). This is a
    real table -- not a fixed TextChoices -- specifically so a Scholarship
    can be linked to MULTIPLE levels at once (most scholarships fund more
    than one level). Manage these from /admin/ -- there are only ever a
    handful, so no public-facing CRUD for this one.
    """
    code = models.SlugField(max_length=20, unique=True)
    label = models.CharField(max_length=50)
    order = models.PositiveSmallIntegerField(default=0, help_text="Controls display order, lower shows first.")

    class Meta:
        ordering = ["order", "label"]

    def __str__(self):
        return self.label


class Country(models.Model):
    code = models.CharField(max_length=2, unique=True, help_text="ISO 3166-1 alpha-2, e.g. 'US'")
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Countries"

    def __str__(self):
        return self.name

class Scholarship(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, unique=True, blank=True)
    description = models.TextField()

    levels = models.ManyToManyField(
        Level,
        blank=True,
        related_name="scholarships",
        help_text="Select every level this scholarship funds (most fund more than one).",
    )
    funding_type = models.CharField(
        max_length=20,
        choices=FundingType.choices,
        default=FundingType.FULLY_FUNDED,
        db_index=True,
    )
    application_fee_required = models.BooleanField(
        default=False,
        help_text="Does the applicant need to pay a fee to apply?",
    )

    nationality_scope = models.CharField(
        max_length=10,
        choices=NationalityScope.choices,
        default=NationalityScope.ALL,
        help_text="Choose 'Specific Countries Only' to restrict eligibility below.",
    )
    eligible_countries = models.ManyToManyField(
        Country,
        blank=True,
        related_name="scholarships",
        help_text="Leave empty if 'Open to All Nationalities' is selected.",
    )

    university = models.CharField(max_length=255, help_text="University or organization name")
    logo = models.ImageField(upload_to="scholarship_logos/", blank=True, null=True)

    application_link = models.URLField()
    deadline = models.DateField(db_index=True)

    is_active = models.BooleanField(
        default=True,
        help_text="Manually unpublish a scholarship without deleting it.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["deadline"]
        indexes = [
            models.Index(fields=["deadline", "is_active"]),
            models.Index(fields=["funding_type"]),
        ]

    def __str__(self):
        return f"{self.title} — {self.university}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.title}-{self.university}")[:270]
            slug = base_slug
            counter = 1
            while Scholarship.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                counter += 1
                slug = f"{base_slug}-{counter}"
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("scholarship-detail", kwargs={"slug": self.slug})

    @property
    def is_expired(self) -> bool:
        return self.deadline < timezone.localdate()

    @property
    def is_open(self) -> bool:
        return self.is_active and not self.is_expired


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    bio = models.TextField(max_length=500, blank=True)
    country = models.ForeignKey(
        Country,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="profiles",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile: {self.user}"

class SavedScholarshipStatus(models.TextChoices):
    SAVED = "saved", "Saved"
    APPLIED = "applied", "Applied"
    NOT_INTERESTED = "not_interested", "Not Interested"


class SavedScholarship(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="saved_scholarships",
    )
    scholarship = models.ForeignKey(
        Scholarship,
        on_delete=models.CASCADE,
        related_name="saved_by",
    )
    status = models.CharField(
        max_length=20,
        choices=SavedScholarshipStatus.choices,
        default=SavedScholarshipStatus.SAVED,
    )
    note = models.CharField(max_length=255, blank=True)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "scholarship")
        ordering = ["-saved_at"]

    def __str__(self):
        return f"{self.user} saved {self.scholarship.title}"


class SuccessStory(models.Model):
    """
    A short win-story a user posts about their own scholarship journey.
    Publishes immediately -- no approval queue. `is_published` exists purely
    as an admin escape hatch (hide instead of delete) if something needs to
    come down later; it's not part of any submission workflow.
    """
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="success_stories",
    )
    title = models.CharField(max_length=255)
    story = models.TextField()
    is_published = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Success stories"

    def __str__(self):
        return f"{self.title} — {self.author}"

    def get_absolute_url(self):
        return reverse("story-detail", kwargs={"pk": self.pk})


class Question(models.Model):
    """
    An open Q&A board post. Optionally linked to a scholarship (e.g. 'has
    anyone applied to this one?') but not required -- general questions
    are fine too.
    """
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="questions",
    )
    title = models.CharField(max_length=255)
    body = models.TextField()
    scholarship = models.ForeignKey(
        Scholarship,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="questions",
        help_text="Optional -- link this question to a specific scholarship.",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("question-detail", kwargs={"pk": self.pk})


class Reply(models.Model):
    """A comment/answer underneath a Question. Flat, no nesting/threading."""
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="replies",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="replies",
    )
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        verbose_name_plural = "Replies"

    def __str__(self):
        return f"Reply by {self.author} on {self.question}"

"""
ADD THIS TO THE BOTTOM OF models.py
------------------------------------
Also add this ONE field to your existing SavedScholarship model (don't
create a second SavedScholarship class — just add the field inside the
one you already have):

    reminder_sent = models.BooleanField(
        default=False,
        help_text="Flips to True once a deadline-reminder notification has been sent.",
    )

Then run:
    python manage.py makemigrations
    python manage.py migrate
"""

from django.conf import settings
from django.db import models
from django.urls import reverse


class Notification(models.Model):
    """
    Deliberately simple: one message string + one URL string, instead of a
    GenericForeignKey system. Easier to read while you're learning, and
    still flexible enough to cover replies, comments, and deadline reminders.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    message = models.CharField(max_length=255)
    url = models.CharField(max_length=255, blank=True, help_text="Where clicking this notification should go.")
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"To {self.user}: {self.message}"


class StoryComment(models.Model):
    """A plain-text comment on a SuccessStory. No nesting, no reactions (yet)."""
    story = models.ForeignKey(
        "SuccessStory",
        on_delete=models.CASCADE,
        related_name="comments",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="story_comments",
    )
    body = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment by {self.author} on {self.story}"