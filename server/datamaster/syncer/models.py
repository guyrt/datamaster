from django.db import models

# Create your models here.
class ClientDataSet(models.Model):
    """
    Record of a file created by some local system.
    """

    # A single ClientDataSet entry records that a single user create a single file locally, within context of a team.
    team = models.ForeignKey('teams.Team', on_delete=models.CASCADE)
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE)

    #
    # Facts about the upload
    #

    # Track a hash of the metadata arguments that were assigned to this data file.
    # Empty means no metaargs - this is not necessarily the hash of an empty string.
    metaargs_guid = models.CharField(max_length=256)

    timepath = models.CharField(max_length=256)



class SyncedDataSet(models.Model):
    """Record that a ClientDataSet was uploaded to a storage system."""
    pass
