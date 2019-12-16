from django.contrib.auth.models import User
from django.test import TestCase

from syncer.models import ClientDataSet
from teams.models import Team
from teams import permissions


class TestInitilizers(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='testuser')
        self.team = Team.objects.create(team_name='test1', team_slug='teamslug1')
        permissions.grant_access(self.user, self.team)
        self.branch = permissions.setup_team(self.team)

        self.cds = ClientDataSet.objects.create(
            branch_id=self.branch.id, 
            user=self.user, 
            team=self.team,
            metaargs_guid='abc-123',
            timepath='',
            name='ds1',
            project='p1',
            local_path='p',
            local_machine_name='foo1',
            local_machine_time='2019-12-15'
        )
