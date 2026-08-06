from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

from .models import Profile, Question, Reply, SuccessStory, StoryComment


class SignupForm(UserCreationForm):
    
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["bio", "country"]
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 4, "placeholder": "A little about you…", "maxlength": 500}),
        }


class SuccessStoryForm(forms.ModelForm):
    class Meta:
        model = SuccessStory
        fields = ["title", "story"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "e.g. How I landed a fully-funded Master's"}),
            "story": forms.Textarea(attrs={"rows": 8, "placeholder": "Tell it however you like — the more detail, the more useful it is to the next applicant."}),
        }


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ["title", "body", "scholarship"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "What do you want to ask?"}),
            "body": forms.Textarea(attrs={"rows": 6}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["scholarship"].required = False
        self.fields["scholarship"].empty_label = "Not linked to a specific scholarship"  # type: ignore[attr-defined]


class ReplyForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = ["body"]
        widgets = {
            "body": forms.Textarea(attrs={"rows": 3, "placeholder": "Write a reply…"}),
        }


class StoryCommentForm(forms.ModelForm):
    class Meta:
        model = StoryComment
        fields = ["body"]
        widgets = {
            "body": forms.Textarea(attrs={"rows": 3, "placeholder": "Say something encouraging…"}),
        }
        labels = {"body": ""}