import mss

if __name__ == "__main__":

    with mss.mss() as sct:
        print(type(sct.monitors[0]))
        print(sct.monitors[0])
        print(sct.monitors[1])
        print(sct.monitors[2])
