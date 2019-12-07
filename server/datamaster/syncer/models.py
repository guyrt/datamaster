from django.db import models

from datamaster.core_models import DataMasterModelBaseMixin


class ClientDataSet(DataMasterModelBaseMixin):
    """
    Record of a file created by some local system.
    """

    # A single ClientDataSet entry records that a single user create a single file locally, within context of a team.
    team = models.ForeignKey('teams.Team', on_delete=models.CASCADE)
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE)

    #
    # Facts that determine a unique file
    #

    # Track a hash of the metadata arguments that were assigned to this data file.
    # Empty means no metaargs - this is not necessarily the hash of an empty string.
    metaargs_guid = models.CharField(max_length=256, blank=True)

    # time path section, which acts as a forced folder path element.
    timepath = models.CharField(max_length=256, blank=True)

    # dataset name: must be unique within a project.
    name = models.CharField(max_length=256)

    # dataset project: simple grouping of projects. Handles nesting by "."
    project = models.CharField(max_length=1024, blank=True)

    # local path on local machine where the file was saved
    local_path = models.CharField(max_length=2048)

    # store the fully qualified name of the machine that created the file.
    local_machine_name = models.CharField(max_length=1024)

    # time that object was created on local machine
    local_machine_time = models.DateTimeField()

    class Meta:
        constraints = [
            models.UniqueConstraint (
                fields=['team', 'user', 'metaargs_guid', 'timepath', 'name', 'project'],
                name='rowlevelunique'    
            )
        ]


class SyncedDataSet(DataMasterModelBaseMixin):
    """Record that a ClientDataSet was uploaded to a storage system."""
    pass
