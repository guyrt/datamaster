from context import dm, db, DMTestBase
import unittest
from dm.models import DataSet

import pyarrow.parquet as pq
import pyarrow as pa
import pandas as pd
import numpy as np

class ParquetTests(DMTestBase):

    def test_write_single_parquet_file(self):
        """ Write to and read from a file in parquet format that has one partition """
        df = pd.DataFrame({'one': [-1, np.nan, 2.5],
                       'two': ['foo', 'bar', 'baz'],
                       'three': [True, False, True]},
                       index=list('abc'))
        table = pa.Table.from_pandas(df)
        pq.write_table(table, dm.outputs.parquettest.parquetsingle)

        # read it back in
        table2 = pq.read_table(dm.inputs.parquettest.parquetsingle)
        df2 = table2.to_pandas()
        self.assertEqual(df.shape, df2.shape)

    def test_write_big_parquet(self):
        df = pd.DataFrame({'r': np.random.rand(200000), 'p': [1] * 100000 + [2] * 100000})
        table = pa.Table.from_pandas(df)
        # Note! This requires that we pass in a string.
        pq.write_to_dataset(table, root_path=str(dm.out.parquettest.parquetlarge), partition_cols=['p'])
        # read it back in
        table2 = pq.read_table(dm.inputs.parquettest.parquetlarge)
        df2 = table2.to_pandas()
        self.assertEqual(df.shape, df2.shape)



if __name__ == '__main__':
    unittest.main()