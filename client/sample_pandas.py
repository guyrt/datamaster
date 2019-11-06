import pandas

from dm import out

df = pandas.DataFrame({'a': [1, 2], 'b': [3, 4]})

df.to_csv(out.pandasfile)
