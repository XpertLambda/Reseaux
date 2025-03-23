from obj import *
import pickle

with open("obj.pickle", "rb") as fr:
    obj = pickle.loads(fr.read())

print(obj) # read the object adn compare the results
