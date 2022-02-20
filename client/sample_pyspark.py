from pyspark.sql import SparkSession
from random import randint

from dm import outputs

spark = SparkSession \
    .builder \
    .appName("PySpark dm sample") \
    .getOrCreate()

random_data = [('someName', randint(0, 100)) for i in range(10000)]

df = spark.createDataFrame(random_data, ['names', 'randomInt'])

t = df.write.format('csv')
import pdb; pdb.set_trace()
t.save(outputs.sparkExample3)

