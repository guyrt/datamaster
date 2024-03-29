import os
import unittest
import mock
import json

from .context import DMTestBase
import dm
from dm.models import DataSet, DataSetFactKeys
from dm.cache import DataSetNameCollision


class OutputTests(DMTestBase):

    def state_check(self):
        """ Utility to check that the model state is correct """
        self.assertEqual(DataSet.select().count(), 1)

    def test_create_file(self):
        git_patch = mock.patch("dm.datamaster.MetadataWriter._cache_git_info").start()
        git_patch.return_value = {"git_called": True}
        file_path = dm.outputs.testfile.__fspath__()
        self.assertEqual(os.path.split(file_path)[1], 'testfile')

        self.state_check()
        dataset = DataSet.get()
        self.assertEqual(dataset.name, "testfile")
        self.assertEqual(dataset.project, "")
        self.assertEqual(dataset.branch.name, "master")
        self.assertEqual(os.path.split(dataset.get_fact('localpath'))[1], 'testfile')
        self.assertEqual(0, dataset.last_server_version)
        git_patch.assert_called()
        context_output = json.loads(open(dataset.get_metadata_filename(), 'r').read())
        self.assertTrue(context_output['context']['git_root']['git_called'])

    def test_create_file_with_extension(self):
        file_path = dm.outputs.testfile(extension='json').__fspath__()
        self.assertEqual(os.path.split(file_path)[1], 'testfile.json')

        self.state_check()
        dataset = DataSet.get()
        self.assertEqual(dataset.name, "testfile")
        self.assertEqual(dataset.project, "")
        self.assertEqual(dataset.branch.name, "master")
        self.assertEqual(os.path.split(dataset.get_fact('localpath'))[1], 'testfile.json')
        self.assertEqual(dataset.get_fact(DataSetFactKeys.FileExtension), 'json')

    def test_create_file_with_timefield(self):
        file_path = dm.outputs.testfile(timepath='2019/11/03').__fspath__()
        file_path = file_path.replace('\\', '/')
        self.assertTrue(file_path.endswith('testfile/2019/11/03'))
        
        self.state_check()
        dataset = DataSet.get()
        self.assertEqual(dataset.name, "testfile")
        self.assertEqual(dataset.project, "")
        self.assertEqual(dataset.branch.name, "master")
        self.assertEqual(dataset.get_fact('localpath').replace('\\', '/')[-10:], '2019/11/03')

    def test_create_file_with_timefield_extra_slash(self):
        file_path = dm.outputs.testfile(timepath='2019/11/03/').__fspath__()
        file_path = file_path.replace('\\', '/')
        self.assertTrue(file_path.endswith('testfile/2019/11/03'))

        self.state_check()
        dataset = DataSet.get()
        self.assertEqual(dataset.name, "testfile")
        self.assertEqual(dataset.project, "")
        self.assertEqual(dataset.branch.name, "master")
        self.assertEqual(dataset.get_fact('localpath').replace('\\', '/')[-10:], '2019/11/03')

    def test_create_file_with_timefield_and_project(self):
        file_path = dm.outputs.project.testfile(timepath='2019/11/03').__fspath__()
        file_path = file_path.replace('\\', '/')
        self.assertTrue(file_path.endswith('project/testfile/2019/11/03'))
        
        self.state_check()
        dataset = DataSet.get()
        self.assertEqual(dataset.name, "testfile")
        self.assertEqual(dataset.project, "project")
        self.assertEqual(dataset.branch.name, "master")
        self.assertEqual(dataset.get_fact('localpath').replace('\\', '/')[-10:], '2019/11/03')

    def test_create_file_with_timefield_and_filetype(self):
        file_path = dm.outputs.testfile(timepath='2019/11/03').__fspath__()
        file_path = file_path.replace('\\', '/')
        self.assertTrue(file_path.endswith('testfile/2019/11/03'))
        
        self.state_check()
        dataset = DataSet.get()
        self.assertEqual(dataset.name, "testfile")
        self.assertEqual(dataset.project, "")
        self.assertEqual(dataset.branch.name, "master")
        self.assertEqual(dataset.get_fact('localpath').replace('\\', '/')[-10:], '2019/11/03')

    def test_create_twofiles_with_formats(self):
        file_path_json = dm.outputs.testfile(extension='json').__fspath__()
        self.assertEqual(os.path.split(file_path_json)[1], 'testfile.json')
        file_path = dm.outputs.testfile.__fspath__()
        self.assertEqual(os.path.split(file_path)[1], 'testfile')

        datasets = [f for f in DataSet.select().where(DataSet.name == 'testfile').order_by(DataSet.id)]
        self.assertEqual(len(datasets), 2)
        dataset1 = datasets[0]
        self.assertEqual(dataset1.name, "testfile")
        self.assertEqual(dataset1.project, "")
        self.assertEqual(dataset1.branch.name, "master")
        self.assertEqual(os.path.split(dataset1.get_fact('localpath'))[1], 'testfile.json')

        dataset2 = datasets[1]        
        self.assertEqual(dataset2.name, "testfile")
        self.assertEqual(dataset2.project, "")
        self.assertEqual(dataset2.branch.name, "master")
        self.assertEqual(os.path.split(dataset2.get_fact('localpath'))[1], 'testfile')

    def test_create_file_with_metaargs(self):
        t = dm.outputs.f1(meta={'a': 1})
        f1path1 = t.__fspath__()
        f1path2 = dm.outputs.f1(meta={'a': 2}).__fspath__()

        self.assertNotEqual(f1path1, f1path2, "Different args implies different files")

    def test_create_file_with_metaargs_same_but_diff_order(self):
        t = dm.outputs.f1(meta={'a': 1, 'b': 2e-5})
        f1path1 = t.__fspath__()
        f1path2 = dm.outputs.f1(meta={'b': 2e-5, 'a': 1}).__fspath__()

        self.assertEqual(f1path1, f1path2, "Same args implies same files")

    def test_declare_file_then_project_same_time_same_name_fails(self):
        dm.outputs.f1.__fspath__()
        self.assertRaises(DataSetNameCollision, dm.outputs.f1.f2.__fspath__)

    def test_declare_file_then_project_same_later_same_name_fails(self):
        dm.outputs.f1.__fspath__()
        dm.outputs.p1.p2.f2.__fspath__()
        new_out = dm.DataMasterOutput()
        # try to make a project with original filename
        self.assertRaises(DataSetNameCollision, new_out.f1.f2.__fspath__)
        self.assertRaises(DataSetNameCollision, new_out.p1.p2.f2.f3.__fspath__)

    def test_is_default_on_three_files(self):
        # Set is_default on separate files
        dm.outputs.f1(meta={'a': 1}).__fspath__()
        dm.outputs.f2(meta={'a': 1}).__fspath__()

        dm.outputs.f1(meta={'a': 2}).__fspath__()

        datasets = list(DataSet.select())
        self.assertFalse(datasets[0].is_default)
        self.assertTrue(datasets[1].is_default)
        self.assertTrue(datasets[2].is_default)

        # Getting dm1 should return second copy.
        dm1_output = dm.inputs.f1
        # todo:
#        self.assertEqual('{"a": 2}', dm1_output._dataset.get_metaargs_str())


if __name__ == '__main__':
    unittest.main()