from django.contrib.auth.models import User
from django.test import Client, TestCase

from .initializers import TestInitilizers
from syncer.models import ClientDataSet


class BranchDeleteTests(TestInitilizers):

    def test_delete_branch_deletes(self):
        self.branch.deactivate()
        self.branch.refresh_from_db()
        self.assertFalse(self.branch.is_active)
        self.cds.refresh_from_db()
        self.assertFalse(self.cds.is_active)


class UserDeleteTest(TestInitilizers):

    def test_delete_user_doesnt_delete(self):
        self.user.delete()
        local_cds = ClientDataSet.objects.get(id=self.cds.id)
        self.assertTrue(local_cds.is_active)
        self.assertIsNone(local_cds.user)
