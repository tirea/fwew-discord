#!/usr/bin/env python
import sys
from random import randint


def lukin(nimi_mute):
    output = ""
    for word in nimi_mute:
        dict = open("toki_ponaya_liupuk.txt", "r")
        for line in dict:
            if len(line) != 0:
                fields = line.strip().split("\t")
                tp_word = fields[0]
                nav_word = fields[2]
                if word == tp_word:
                    if "," in nav_word:
                        nav_words = nav_word.strip().split(", ")
                        r = randint(0, len(nav_words) - 1)
                        output += nav_words[r] + " "
                    else:
                        output += nav_word + " "
    return output


if __name__ == '__main__':
    s = lukin(sys.argv[1:])
    print(s)
