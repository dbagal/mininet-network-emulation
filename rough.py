class myclass:
    def __init__(self):
        print("__init__")

    def __enter__(self): 
        print("__enter__")

    def __exit__(self, type, value, traceback):
        print("__exit__")

    def __del__(self):
        print("__del__")

    def temp(self):
        with self():
            print("eebfhe")

with myclass(): 
    print("body")

x = myclass()

with x.temp():
    print("temp called")