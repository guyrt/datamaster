from dm import outputs


# Write a simple file:
f = open(outputs.foo, "w")
f.write("hello")
f.close()

# Write a simple file with a fixed output format
f = open(outputs.bar(extension='json'), "w")
f.write("[]")
f.close()

# Write a file as part of a project
# This should be written to root/myproject/outputone.txt
f = open(outputs.myproject.outputone(extension='txt'), 'w')
f.write("projectoutput")
f.close()

# With kwargs
f = open(outputs.myproject.outputtwo(meta={'lr': 2e-5, 'epochs': 3}), 'w')
f.write("out")
f = open(outputs.myproject.outputtwo(meta={'lr': 2e-5, 'epochs': 5}), 'w')
f.write('out2')
f = open(outputs.myproject.outputtwo(meta={'lr': 2e-5, 'epochs': 3}), 'w')
f.write('outreplace')
f = open(
    outputs.myproject.innerproject.outputthree(meta={'lr': 2e-5, 'epochs': 3}), 
    'w'
)
f.write('outputthree')

# With timestamps
f = open(outputs.withtime.model(meta={'lr': 2e-5}, timepath='2019/11/03'), 'w')
f.write("Nov 3")
f = open(outputs.withtime.model(meta={'lr': 2e-5}, timepath='2019/11/04'), 'w')
f.write("Nov 4")

# Second copy
f = open(outputs.withtime.model(timepath='2019/11/03'), 'w')
f.write("Nov 3")
f = open(outputs.withtime.model(timepath='2019/11/04'), 'w')
f.write("Nov 4")

