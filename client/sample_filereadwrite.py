from dm import inputs, out

f1 = open(inputs.foo, 'r')

f2 = open(out.foocopy, "w")
f2.write(f1.read())
f2.close()
