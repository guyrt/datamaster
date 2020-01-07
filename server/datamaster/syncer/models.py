from django.db import models

from datamaster.core_models import DataMasterModelBaseMixin


default_branch_name = "master"


class ClientBranch(DataMasterModelBaseMixin):
    """Record of a client-side Branch that was created within a team.
    
    Teams share branches, with "last wins" on most create behaviors within a branch.
    """

    created_by = models.ForeignKey("auth.User", on_delete=models.SET_NULL, blank=True, null=True)
    team = models.ForeignKey('teams.Team', on_delete=models.CASCADE)
    name = models.CharField(max_length=256)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['team', 'name'],
                name='teamlevelunique'
            )
        ]

    def deactivate(self):
        self.is_active = False
        self.clientdataset_set.update(is_active=False)
        self.save()


class ClientDataSet(DataMasterModelBaseMixin):
    """
    Record of a file created by some local system.
    """

    # A single ClientDataSet entry records that a single user create a single file locally, within context of a team.
    team = models.ForeignKey('teams.Team', on_delete=models.CASCADE)
    user = models.ForeignKey("auth.User", on_delete=models.SET_NULL, blank=True, null=True)

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

    # client-side active branch, which should match a synced branch locally.
    branch = models.ForeignKey(ClientBranch, on_delete=models.CASCADE)

    # guid from originator of a dataset
    local_machine_guid = models.CharField(max_length=36)

    class Meta:
        constraints = [
            models.UniqueConstraint (
                fields=['team', 'user', 'metaargs_guid', 'timepath', 'name', 'project', 'branch'],
                name='rowlevelunique'    
            ),
            models.UniqueConstraint(
                fields=['local_machine_guid'],
                name='localmachienguidunique'
            )
        ]


class ClientDataSetFact(DataMasterModelBaseMixin):
    clientdataset = models.ForeignKey(ClientDataSet, related_name='facts', on_delete=models.CASCADE)

    key = models.CharField(max_length=256)

    value = models.TextField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['clientdataset', 'key'],
                name='ClientDataSetKey'
            )
        ]


class SyncedDataSet(DataMasterModelBaseMixin):
    """Record that a ClientDataSet was uploaded to a storage system."""
    pass


