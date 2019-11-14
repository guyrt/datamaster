from context import dm, test_db, DMTestBase
import unittest
from dm.models import DataSet


class InputTests(DMTestBase):

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


if __name__ == '__main__':
    unittest.main()