from dm import out

# Write a simple file:
f = open(out.foo, "w")
f.write("hello")
f.close()

# Write a simple file with a fixed output format
f = open(out.bar(format='json'), "w")
f.write("[]")
f.close()

# Write a file as part of a project
# This should be written to root/myproject/output1.txt
f = open(out.myproject.outputone, 'w')
f.write("projectoutput")
f.close()

# With kwargs
f = open(out.myproject.outputtwo(meta={'lr': 2e-5, 'epochs': 3}), 'w')
f.write("out")
f = open(out.myproject.outputtwo(meta={'lr': 2e-5, 'epochs': 5}), 'w')
f.write('out2')
f = open(out.myproject.outputtwo(meta={'lr': 2e-5, 'epochs': 3}), 'w')
f.write('outreplace')
f = open(out.myproject.innerproject.outputthree(meta={'lr': 2e-5, 'epochs': 3}), 'w')
f.write('outputthree')

#
#f = open(out.myproject.innerproject.outputone(meta={'lr': 2e-5, 'epochs': 3}), 'w')
#f.write('outreplace')
