import pickle
import json
sensor = {
    "nome": "mateus",
    "id": "merda",
}

sensor2 = {
    "nome": "maruzka",
    "id": "bosta"
}


with open("30_04_2022.pickle", "rb") as f:
    while True:
        try:
            a = pickle.load(f)
            print(a)
            print("'")
        except:
            break
