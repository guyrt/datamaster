from dm import inputs


#print(inputs.parquetproject.rawdata.__doc__)


print(f"Default is {str(inputs.parquetproject.rawdata)}")

print(f"With range is {inputs.parquetproject.rawdata.timerange('2022/01/*')}")
