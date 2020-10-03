csv = open("input.csv", "r").read().split("\n")[1:]
formatted = list()
def func(inp):
    for line in inp:
        id, image, correct, tags = line.split("	")
        tags = [item.replace("'","\"") for item in tags.split(" ")]
        formatted = ("      {\n\"id\": \"%s\",\n\"image\":\"%s\",\n\"correct\":\"%s\",\n\"tags\":%s\n},\n" % (id, image, correct, tags)).replace("'","\"").replace("\n","\n      ")
        print(formatted)

func(csv)