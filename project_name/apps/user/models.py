from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from {{ project_name }}.apps.core.models import Base, create_default_hash


class Profile(Base):
    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


# create user profile on the fly
@receiver(post_save, sender=User)
def create_profile(sender, **kwargs):
    user = kwargs['instance']
    if kwargs['created']:
        profile = Profile(user=user)
        profile.save()


@receiver(post_delete, sender=Profile)
def delete_user(sender, instance=None, **kwargs):
    try:
        instance.user
    except User.DoesNotExist:
        pass
    else:
        instance.user.delete()
