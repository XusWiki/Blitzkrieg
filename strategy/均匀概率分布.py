import numpy as np
import pandas as pd

def strategy_long(index_1, index_2, index_3):
    if index_1:
        return 0
    elif index_2:
        return 1
    elif index_3:
        return 0
        
def strategy_short(index_4, index_5, index_6)        