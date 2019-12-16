from django.contrib.auth.models import User
from django.test import Client, TestCase

from .initializers import TestInitilizers


class BranchTests(TestInitilizers):

    def test_delete_branch_deletes(self):
        self.branch.deactivate()
        self.branch.refresh_from_db()
        self.assertFalse(self.branch.is_active)
        self.cds.refresh_from_db()
        self.assertFalse(self.cds.is_active)
