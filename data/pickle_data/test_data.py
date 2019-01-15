import csv
import os
import numpy as np
import random
import cPickle as pickle


file_name = "test.pickle"
with open(file_name, 'rb') as f:
    data = pickle.load(f)
    print data['feature']
    print data['label']
    print len(data['feature'])
    print len(data['feature'][0])
    print len(data['label'][0])