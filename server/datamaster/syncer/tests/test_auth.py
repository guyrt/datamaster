from datetime import datetime
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import Client, TestCase

from datamaster.teams import permissions
from datamaster.syncer.models import ClientDataSet, ClientBranch


class SyncAuthTests(TestCase):

    def __init__(self):
        self.user = User.objects.create(username='testuser')
        self.team = Team.objects.create(team_name='test1', team_slug='teamslug1')
        self.permissions.grant_access(self.user, self.team)
        self.branch = setup_team(self.team)

        self.cds = ClientDataSet.objects.create(
            branch=self.branch, 
            user=self.user, 
            team=self.team,
            metaargs_guid='abc-123',
            timepath='',
            name='ds1',
            project='p1',
            local_path='p',
            local_machine_name='foo1',
            local_machine_team=datetime.now
        )

    def test_dataset_list_with_auth(self):
        url = reverse('dataset-list')
        response = Client.get(url)


