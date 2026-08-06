from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile


@receiver(post_save, sender=User)
def create_profile_for_new_user(sender, instance, created, **kwargs):
    
    if created:
        Profile.objects.create(user=instance)

"""
ADD THIS TO THE BOTTOM OF signals.py
--------------------------------------
These two receivers create a Notification the moment someone replies to a
question, or comments on a success story -- as long as they're not just
replying/commenting on their own post (no point notifying yourself).

Make sure Reply and StoryComment are imported at the top of signals.py:
    from .models import Notification, Reply, StoryComment
"""

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Notification, Reply, StoryComment


@receiver(post_save, sender=Reply)
def notify_on_reply(sender, instance, created, **kwargs):
    if not created:
        return
    question = instance.question
    if instance.author_id == question.author_id:
        return  # don't notify someone about their own reply

    Notification.objects.create(
        user=question.author,
        message=f'{instance.author.username} replied to your question "{question.title}"',
        url=question.get_absolute_url(),
    )


@receiver(post_save, sender=StoryComment)
def notify_on_story_comment(sender, instance, created, **kwargs):
    if not created:
        return
    story = instance.story
    if instance.author_id == story.author_id:
        return

    Notification.objects.create(
        user=story.author,
        message=f'{instance.author.username} commented on your story "{story.title}"',
        url=story.get_absolute_url(),
    )