from obj import *
import pickle


aosend = AObj("hello")
bosend = BObj(aosend, 1)

pyosend = PyObj(aosend, bosend, [3,4])

# dump object.pickle
# start porcc c

print(f"to send :{pyosend}")


with open("obj.pickle", "wb") as fw:
    pickle.dump(pyosend, fw)

print("obj written to file")
