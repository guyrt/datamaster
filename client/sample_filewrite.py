from dm import out

# Write a simple file:
f = open(out.foo, "w")
f.write("hi")
f.close()

# Write a simple file with a fixed output format
f = open(out.bar('json'), "w")
f.write("[]")
f.close()

# Write a file as part of a project
# This should be written to root/myproject/output1.txt
f = open(out.myproject.output1, 'w')
f.write("projectoutput")
f.close()

