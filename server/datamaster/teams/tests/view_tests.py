from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from rest_framework.authtoken.models import Token

from syncer.models import ClientDataSet
from teams.models import Team
from teams import permissions


class AuthTests(TestCase):

    def test_only_user_can_access_users(self):
        user1 = User.objects.create(username='testuser')
        user2 = User.objects.create(username='othertestuser')
        token = Token.objects.create(user=user1)

        client = Client(HTTP_AUTHORIZATION='Token {0}'.format(token.key))
        user_url = reverse('user-details', args=(user1.username, ))
        response = client.get(user_url)

        self.assertEqual(response.status_code, 200)
        other_user_url = reverse('user-details', args=(user2.username, ))
        response = client.get(other_user_url)
        self.assertEqual(response.status_code, 404)

