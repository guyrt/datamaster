from datetime import datetime
from django.contrib.auth.models import User
from django.urls import reverse
from django.test import Client
from rest_framework.authtoken.models import Token

from teams import permissions
from syncer.models import ClientDataSet, ClientBranch
from teams.models import Team, Membership
from .initializers import TestInitilizers


class SyncAuthTests(TestInitilizers):

    def setUp(self):
        super(SyncAuthTests, self).setUp()
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

    def test_dataset_detail_get_with_auth(self):

        url = reverse('clientdataset-detail', args=(self.team.team_slug, self.cds.id))
        response = self.client.get(url)

        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.assertEqual(self.cds.name, payload['name'])

    def test_dataset_list_fails_no_auth(self):

        url = reverse('clientdataset-list', args=(self.team.team_slug, ))
        new_client = Client()  # no auth set.
        response = new_client.get(url)

        self.assertEqual(401, response.status_code)
        self.assertTrue('detail' in response.json())
        
    def test_dataset_detail_fails_no_auth(self):

        url = reverse('clientdataset-detail', args=(self.team.team_slug, self.cds.id))
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
    
    def test_dataset_detail_fails_if_not_on_team(self):

        # Remove authorization to the team.
        Membership.objects.filter(user=self.user, team=self.team).delete()

        url = reverse('clientdataset-detail', args=(self.team.team_slug, self.cds.id))
        new_client = Client()  # no auth set.
        response = new_client.get(url)

        self.assertEqual(401, response.status_code)
        self.assertTrue('detail' in response.json())