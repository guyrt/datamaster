from context import dm, test_db, DMTestBase
import unittest
from dm.models import DataSet
from dm.cache import DataSetNameCollision


class OutputTests(DMTestBase):

    def state_check(self):
        """ Utility to check that the model state is correct """
        self.assertEqual(DataSet.select().count(), 1)

    def test_create_file(self):
        file_path = dm.out.testfile.__fspath__()
        self.assertEqual(file_path[-9:], '/testfile')

        self.state_check()
        dataset = DataSet.get()
        self.assertEqual(dataset.name, "testfile")
        self.assertEqual(dataset.project, "")
        self.assertEqual(dataset.get_fact('localpath')[-9:], '/testfile')
        self.assertEqual(dataset.get_fact('calling_filename'), 'outputer_tests.py')
        self.assertIsNone(dataset.get_fact('metaargfilename'))  # is None because we didn't declare metaargs or format

    def test_create_file_with_filetype(self):
        file_path = dm.out.testfile(format='json').__fspath__()
        self.assertEqual(file_path[-14:], '/testfile.json')

        self.state_check()
        dataset = DataSet.get()
        self.assertEqual(dataset.name, "testfile")
        self.assertEqual(dataset.project, "")
        self.assertEqual(dataset.get_fact('localpath')[-14:], '/testfile.json')
        self.assertEqual(dataset.get_fact('calling_filename'), 'outputer_tests.py')
        self.assertIsNotNone(dataset.get_fact('metaargfilename'))

    def test_create_twofiles_with_formats(self):
        file_path_json = dm.out.testfile(format='json').__fspath__()
        self.assertEqual(file_path_json[-14:], '/testfile.json')
        file_path = dm.out.testfile.__fspath__()
        self.assertEqual(file_path[-9:], '/testfile')

        datasets = [f for f in DataSet.select().where(DataSet.name == 'testfile').order_by(DataSet.id)]
        self.assertEqual(len(datasets), 2)
        dataset1 = datasets[0]
        self.assertEqual(dataset1.name, "testfile")
        self.assertEqual(dataset1.project, "")
        self.assertEqual(dataset1.get_fact('localpath')[-14:], '/testfile.json')
        self.assertEqual(dataset1.get_fact('calling_filename'), 'outputer_tests.py')
        self.assertIsNotNone(dataset1.get_fact('metaargfilename'))

        dataset2 = datasets[1]        
        self.assertEqual(dataset2.name, "testfile")
        self.assertEqual(dataset2.project, "")
        self.assertEqual(dataset2.get_fact('localpath')[-9:], '/testfile')
        self.assertEqual(dataset2.get_fact('calling_filename'), 'outputer_tests.py')
        self.assertIsNone(dataset2.get_fact('metaargfilename'))  # is None because we didn't declare metaargs or format

    def test_create_file_with_metaargs(self):
        t = dm.out.f1(meta={'a': 1})
        f1path1 = t.__fspath__()
        f1path2 = dm.out.f1(meta={'a': 2}).__fspath__()

        self.assertNotEqual(f1path1, f1path2, "Different args implies different files")

    def test_declare_file_then_project_same_time_same_name_fails(self):
        dm.out.f1.__fspath__()
        self.assertRaises(DataSetNameCollision, dm.out.f1.f2.__fspath__)

    def test_declare_file_then_project_same_later_same_name_fails(self):
        dm.out.f1.__fspath__()
        dm.out.p1.p2.f2.__fspath__()
        new_out = dm.DataMasterOutput()
        # try to make a project with original filename
        self.assertRaises(DataSetNameCollision, new_out.f1.f2.__fspath__)
        self.assertRaises(DataSetNameCollision, new_out.p1.p2.f2.f3.__fspath__)

if __name__ == '__main__':
    unittest.main()