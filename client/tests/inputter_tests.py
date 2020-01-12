from context import dm, db, DMTestBase
import unittest
from dm.models import DataSet


class InputTests(DMTestBase):
    # pylint: disable=no-member

    def test_nested(self):
        ''' Build nested structure '''

        # creates a tested structure
        dm.out.f1.__fspath__()
        dm.out.p1.f2.__fspath__()
        dm.out.p1.p2.f3.__fspath__()
        dm.out.p1.p2.p3.p4.p5.f6.__fspath__()

        dm.out.p1.p2.p3.fnotused

        self.assertEqual(dm.inputs.f1._name, 'f1')
        self.assertEqual(dm.inputs.p1._project_name, 'p1')
        self.assertEqual(dm.inputs.p1.f2._name, 'f2')
        self.assertEqual(dm.inputs.p1.p2._project_name, 'p2')
        self.assertEqual(dm.inputs.p1.p2.p3._project_name, 'p3')
        self.assertEqual(dm.inputs.p1.p2.p3.p4.p5.f6._name, 'f6')

        self.assertFalse(hasattr(dm.inputs.p1.p2.p3, 'fnotused'))

    def test_two_with_args(self):
        """ Given two files with metaargs, select each one by name and by default """

        f1path1 = dm.out.f1(meta={'arg': 1}).__fspath__()
        f1path2 = dm.out.f1(meta={'arg': 2}).__fspath__()

        self.assertNotEqual(f1path1, f1path2, "Sanity check that paths differ")

        
        self.assertEqual(dm.inputs.f1.__fspath__(), f1path2, "Get default path by create order")
        self.assertRaises(ValueError, dm.inputs.f1)
        self.assertEqual(dm.inputs.f1(meta={'arg': 1}).__fspath__(), f1path1, "Get non default by args")
        self.assertEqual(dm.inputs.f1(meta={'arg': 2}).__fspath__(), f1path2, "Get default by args")

    def test_with_without_args(self):
        """ Given with and without args, should return either. Tests both orders of create """
        fpath1 = dm.out.f1().__fspath__()
        fpath2 = dm.out.f1(meta={'arg': 2}).__fspath__()

        self.assertEqual(dm.inputs.f1.__fspath__(), fpath2, "Get default path by create order")
        self.assertEqual(dm.inputs.f1().__fspath__(), fpath1, "Get default path by create order")
        self.assertEqual(dm.inputs.f1(meta={'arg': 2}).__fspath__(), fpath2, "Get default by args")

        # Do opposite order
        fpath3 = dm.out.f3(meta={'arg': 2}).__fspath__()
        fpath4 = dm.out.f3().__fspath__()
        
        self.assertEqual(dm.inputs.f3.__fspath__(), fpath4, "Get default path by create order")
        self.assertEqual(dm.inputs.f3().__fspath__(), fpath4, "Get default path by create order")
        self.assertEqual(dm.inputs.f3(meta={'arg': 2}).__fspath__(), fpath3, "Get default by args")

    def test_get_right_datetime(self):
        fpath1 = dm.out.f1(timepath='2020/01/03').__fspath__()
        fpath2 = dm.out.f1(timepath='2020/01/04').__fspath__()

        # get the most recent
        default_path = dm.inputs.f1().__fspath__()
        self.assertIn('04', default_path)

        path_02 = dm.inputs.f1(timepath='2020/01/04').__fspath__()
        self.assertIn('04', path_02)
        path_01 = dm.inputs.f1(timepath='2020/01/03').__fspath__()
        self.assertIn('03', path_01)


if __name__ == '__main__':
    unittest.main()