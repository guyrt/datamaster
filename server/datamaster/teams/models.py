from django.db import models

from datamaster.core_models import DataMasterModelBaseMixin


class MembershipType(object):

    ADMIN = "admin"  # Full permissions, including payment and adding/deleting membership
    EDIT = "edit"  # Can edit content, but can not edit account.

    CHOICES = (
        (ADMIN, "Admin"),
        (EDIT, "Members"),
    )


class Team(DataMasterModelBaseMixin):
    """ Tracks a team, which is the main organizational unit in DataMaster """

    team_name = models.CharField(max_length=256)
    team_slug = models.CharField(max_length=64)  # unique organization slug suitable for use in urls.


class Membership(DataMasterModelBaseMixin):
    """ Many to many table representing relationship between User and an organization. """
    
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    relationship_type = models.CharField(max_length=64, choices=MembershipType.CHOICES, default=MembershipType.EDIT)
    