import os
import unittest

from context import dm, db, DMTestBase
from dm.models import DataSet, Branch
from dm.branch_utils import set_branch


class BranchTests(DMTestBase):

    def test_create_branch(self):
        original_branch = Branch.get()
        self.assertEqual(original_branch.name, dm.settings.active_branch)

        dm.cache.cache.get_or_create_branch(dm.settings.active_branch)
        self.assertEqual(Branch.select().count(), 1, "Creating doesn't duplicate")

        dm.cache.cache.get_or_create_branch("test")
        self.assertEqual(Branch.select().count(), 2, "Creating doesn't duplicate")

    def test_save_to_different_branch(self):
        original_branch = Branch.get()
        f1 = dm.out.file.__fspath__()
        set_branch("test")
        f2 = dm.out.file.__fspath__()

        self.assertNotEqual(f1, f2)
        datasets = [f for f in DataSet.select().order_by(DataSet.id)]
        ds1 = datasets[0]
        ds2 = datasets[1]

        self.assertEqual(ds1.branch, original_branch)
        self.assertEqual(ds2.branch.name, dm.settings.active_branch)

        # Both are default in their branch
        self.assertTrue(ds1.is_default)
        self.assertTrue(ds2.is_default)


if __name__ == '__main__':
    unittest.main()