import csv
import os
import numpy as np
import random
import cPickle as pickle


data_path = "../"

train_data = []
test_data = []

def process_time(time_str):

    #
    if time_str.__contains__("/"):
        time_str = time_str.split(" ")[1]

    time_list = time_str.split(":")
    try:
        h = time_list[0]
        m = time_list[1]
    except:
        print time_str

    return float(h) + float(m)/60

def prepare_data(file_name, save_name):
    features = []
    labels = []
    with open(file_name) as of:
        csv_reader = csv.reader(of)
        csv_header = next(csv_reader)
        print len(csv_header)
        for row in csv_reader:
            row_data = []
            for item in row:
                if item.__contains__(":"):
                    row_data.append(process_time(item))
                elif item.__contains__("-"):
                    row_data.append(process_time(item.split("-")[0]))
                    row_data.append(process_time(item.split("-")[1]))
                else:
                    row_data.append(float(item))
            print row_data[1:-1], row_data[-1:]
            features.append(row_data[1: -1])
            labels.append(row_data[-1:])

        of.close()


    with open(save_name, "wb") as sf:
        pickle.dump({"feature": np.array(features), "label": np.array(labels)}, sf)

train_file_name = os.path.join(data_path, "fill_zero_train.csv")
train_save_name = "train.pickle"

test_file_name = os.path.join(data_path, "fill_zero_test.csv")
test_save_name = "test.pickle"

prepare_data(train_file_name, train_save_name)
# prepare_data(test_file_name, test_save_name)

