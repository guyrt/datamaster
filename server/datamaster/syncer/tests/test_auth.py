from datetime import datetime
from django.contrib.auth.models import User
from django.urls import reverse
from django.test import Client, TestCase
from rest_framework.authtoken.models import Token

from teams import permissions
from syncer.models import ClientDataSet, ClientBranch
from teams.models import Team, Membership


class SyncAuthTests(TestCase):

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

        # Token means this user can auth.
        self.token = Token.objects.create(user=self.user)
        self.client = Client(HTTP_AUTHORIZATION='Token {0}'.format(self.token.key))

    def test_dataset_list_with_auth(self):

        url = reverse('clientdataset-list', args=(self.team.team_slug, ))
        response = self.client.get(url)

        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.assertEqual(1, len(payload))
        self.assertEqual(self.cds.name, payload[0]['name'])

    def test_dataset_list_fails_no_auth(self):

        url = reverse('clientdataset-list', args=(self.team.team_slug, ))
        new_client = Client()  # no auth set.
        response = new_client.get(url)

        self.assertEqual(401, response.status_code)
        self.assertTrue('detail' in response.json())
    
    def test_dataset_list_fails_if_not_on_team(self):

        # Remove authorization to the team.
        Membership.objects.filter(user=self.user, team=self.team).delete()

        url = reverse('clientdataset-list', args=(self.team.team_slug, ))
        new_client = Client()  # no auth set.
        response = new_client.get(url)

        self.assertEqual(401, response.status_code)
        self.assertTrue('detail' in response.json())
    