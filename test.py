

def asd():
    a = 3
    try :
        print(a/0)
    except Exception as ex:
        print(ex, str(a))

asd()