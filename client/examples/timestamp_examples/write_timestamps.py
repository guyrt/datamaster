from datetime import datetime

from scipy import rand
from dm import outputs
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import random
import datetime


def write_days(dates, meta_args=None):
    for date in dates:
        datetime_converted = datetime.datetime.strptime(date, 'year=%Y/month=%m/day=%d')
        data = {
            'timestamp': [str(datetime_converted + datetime.timedelta(seconds=random.randint(0, 60 * 60 * 24))) for i in range(100)],
            'event': [random.choice(['start', 'continue', 'quit']) for i in range(100)],
            'p': [random.choice(['a', 'b']) for i in range(100)]
        }
        
        df = pd.DataFrame(data)
        table = pa.Table.from_pandas(df)
        if meta_args:
            pq.write_to_dataset(table, root_path=str(outputs.parquetproject.rawdatawithmetaargs(timepath=date, meta=meta_args)), partition_cols=['p'])
            pq.write_to_dataset(table, root_path=str(outputs.parquetprojectnopart.rawdatawithmetaargs(timepath=date, meta=meta_args)))
        else:
            pq.write_to_dataset(table, root_path=str(outputs.parquetproject.rawdata(timepath=date)), partition_cols=['p'])
            pq.write_to_dataset(table, root_path=str(outputs.parquetprojectnopart.rawdata(timepath=date)))


write_days(["year=2022/month=01/day=01", "year=2022/month=01/day=02", "year=2022/month=01/day=03", "year=2022/month=01/day=04"])

write_days(["year=2022/month=01/day=01", "year=2022/month=01/day=02", "year=2022/month=01/day=03", "year=2022/month=01/day=04"], {'meta1': 2, 'meta2': 3.0})
