from dm import out

print("start")
f = open(out.foo, "w")
print("1")
f.write("hi")
f.close()
print("2")
f = open(out.bar.json, "w")
f.write("hi")

f.close()
