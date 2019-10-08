from collections import Counter
import pprint


def func(x, y):
    if x > y:
        if y > 0:
            return x
        else:
            return y
    return x * y


class Ball:
    
    def __init__(self, color, x, y):
        self.color = color
        self.x = x
        self.y = y
        
    def roll(self, n):
        self.x += n
