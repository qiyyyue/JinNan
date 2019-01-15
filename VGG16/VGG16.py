# -*- coding:utf-8 -*-
import tensorflow as tf
import numpy as np
import time
import os
import sys
import random
import cPickle as pickle



# class_num = 10
# image_size = 32
# img_channels = 3
feature_num = 49
iterations = 28
batch_size = 50
total_epoch = 128
weight_decay = 0.0003
dropout_rate = 0.5
momentum_rate = 0.9
log_save_path = './vgg_16_logs'
model_save_path = './model/vgg_v4/vgg_v4'
data_dir = '../data/pickle_data'



def load_data(file_name):
    with open(file_name, 'rb') as r:
        data = pickle.load(r)
        x = data['feature']
        y = data['label']
        r.close()


    if len(x[0]) < feature_num:
        pad_arr = np.zeros((len(x), feature_num-len(x[0])))
        x = np.append(x, pad_arr, axis=1)
    return x, y

def prepare_data():
    train_file = os.path.join(data_dir, "train.pickle")

    x, y = load_data(train_file)
    x = x.reshape((len(x), 7, 7, 1))
    # y = y.reshape(len(y))
    print x.shape
    print y.shape

    train_x = x
    train_y = y

    # train_x = x[:1000]
    # train_y = y[:1000]

    test_x = x[1000:]
    test_y = y[1000:]

    return train_x, train_y, test_x, test_y

def bias_variable(shape):
    initial = tf.constant(0.1, shape=shape, dtype=tf.float32)
    return tf.Variable(initial)

def conv2d(x, W):
    return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='SAME')

def max_pool(input, k_size=1, stride=1, name=None):
    return tf.nn.max_pool(input, ksize=[1, k_size, k_size, 1], strides=[1, stride, stride, 1],
                          padding='SAME', name=name)

def batch_norm(input):
    return tf.contrib.layers.batch_norm(input, decay=0.9, center=True, scale=True, epsilon=1e-3,
                                        is_training=train_flag, updates_collections=None)

def _random_crop(batch, crop_shape, padding=None):
    oshape = np.shape(batch[0])


    if padding:
        oshape = (oshape[0] + 2*padding, oshape[1] + 2*padding)
    new_batch = []
    npad = ((padding, padding), (padding, padding), (0, 0))
    for i in range(len(batch)):
        new_batch.append(batch[i])
        if padding:
            new_batch[i] = np.lib.pad(batch[i], pad_width=npad,
                                      mode='constant', constant_values=0)
        nh = random.randint(0, oshape[0] - crop_shape[0])
        nw = random.randint(0, oshape[1] - crop_shape[1])
        new_batch[i] = new_batch[i][nh:nh + crop_shape[0],
                                    nw:nw + crop_shape[1]]
    return new_batch

def _random_flip_leftright(batch):
        for i in range(len(batch)):
            if bool(random.getrandbits(1)):
                batch[i] = np.fliplr(batch[i])
        return batch

def learning_rate_schedule(epoch_num):
    if epoch_num < 81:
        return 0.1
    elif epoch_num < 121:
        return 0.01
    else:
        return 0.001




def run_testing(sess, ep):
    loss = 0.0
    pre_index = 0
    add = 20
    for it in range(10):
        batch_x = test_x[pre_index:pre_index+add]
        batch_y = test_y[pre_index:pre_index+add]
        pre_index = pre_index + add
        loss_  = sess.run(mse_lose,
                                feed_dict={x: batch_x, y_: batch_y, keep_prob: 1.0, train_flag: False})
        loss += loss_ / 10.0
    summary = tf.Summary(value=[tf.Summary.Value(tag="test_loss", simple_value=loss)])
    return loss, summary


if __name__ == '__main__':


    train_x, train_y, test_x, test_y = prepare_data()

    # define placeholder x, y_ , keep_prob, learning_rate
    x = tf.placeholder(tf.float32,[None, 7, 7, 1])
    y_ = tf.placeholder(tf.float32, [None, 1])
    keep_prob = tf.placeholder(tf.float32)
    learning_rate = tf.placeholder(tf.float32)
    train_flag = tf.placeholder(tf.bool)

    # build_network
    W_conv1_1 = tf.get_variable('conv1_1', shape=[3, 3, 1, 64], initializer=tf.contrib.keras.initializers.he_normal())
    b_conv1_1 = bias_variable([64])
    output = tf.nn.relu(batch_norm(conv2d(x, W_conv1_1) + b_conv1_1))


    W_conv1_2 = tf.get_variable('conv1_2', shape=[3, 3, 64, 64], initializer=tf.contrib.keras.initializers.he_normal())
    b_conv1_2 = bias_variable([64])
    output = tf.nn.relu(batch_norm(conv2d(output, W_conv1_2) + b_conv1_2))
    output = max_pool(output, 2, 2, "pool1")


    W_conv2_1 = tf.get_variable('conv2_1', shape=[3, 3, 64, 128], initializer=tf.contrib.keras.initializers.he_normal())
    b_conv2_1 = bias_variable([128])
    output = tf.nn.relu(batch_norm(conv2d(output, W_conv2_1) + b_conv2_1))


    W_conv2_2 = tf.get_variable('conv2_2', shape=[3, 3, 128, 128], initializer=tf.contrib.keras.initializers.he_normal())
    b_conv2_2 = bias_variable([128])
    output = tf.nn.relu(batch_norm(conv2d(output, W_conv2_2) + b_conv2_2))
    output = max_pool(output, 2, 2, "pool2")


    W_conv3_1 = tf.get_variable('conv3_1', shape=[3, 3, 128, 256], initializer=tf.contrib.keras.initializers.he_normal())
    b_conv3_1 = bias_variable([256])
    output = tf.nn.relu( batch_norm(conv2d(output,W_conv3_1) + b_conv3_1))


    W_conv3_2 = tf.get_variable('conv3_2', shape=[3, 3, 256, 256], initializer=tf.contrib.keras.initializers.he_normal())
    b_conv3_2 = bias_variable([256])
    output = tf.nn.relu(batch_norm(conv2d(output, W_conv3_2) + b_conv3_2))


    W_conv3_3 = tf.get_variable('conv3_3', shape=[3, 3, 256, 256], initializer=tf.contrib.keras.initializers.he_normal())
    b_conv3_3 = bias_variable([256])
    output = tf.nn.relu( batch_norm(conv2d(output, W_conv3_3) + b_conv3_3))
    output = max_pool(output, 2, 2, "pool3")


    W_conv4_1 = tf.get_variable('conv4_1', shape=[3, 3, 256, 512], initializer=tf.contrib.keras.initializers.he_normal())
    b_conv4_1 = bias_variable([512])
    output = tf.nn.relu(batch_norm(conv2d(output, W_conv4_1) + b_conv4_1))


    W_conv4_2 = tf.get_variable('conv4_2', shape=[3, 3, 512, 512], initializer=tf.contrib.keras.initializers.he_normal())
    b_conv4_2 = bias_variable([512])
    output = tf.nn.relu(batch_norm(conv2d(output, W_conv4_2) + b_conv4_2))


    W_conv4_3 = tf.get_variable('conv4_3', shape=[3, 3, 512, 512], initializer=tf.contrib.keras.initializers.he_normal())
    b_conv4_3 = bias_variable([512])
    output = tf.nn.relu(batch_norm(conv2d(output, W_conv4_3) + b_conv4_3))
    # output = max_pool(output, 2, 2)


    W_conv5_1 = tf.get_variable('conv5_1', shape=[3, 3, 512, 512], initializer=tf.contrib.keras.initializers.he_normal())
    b_conv5_1 = bias_variable([512])
    output = tf.nn.relu(batch_norm(conv2d(output, W_conv5_1) + b_conv5_1))


    W_conv5_2 = tf.get_variable('conv5_2', shape=[3, 3, 512, 512], initializer=tf.contrib.keras.initializers.he_normal())
    b_conv5_2 = bias_variable([512])
    output = tf.nn.relu(batch_norm(conv2d(output, W_conv5_2) + b_conv5_2))


    W_conv5_3 = tf.get_variable('conv5_3', shape=[3, 3, 512, 512], initializer=tf.contrib.keras.initializers.he_normal())
    b_conv5_3 = bias_variable([512])
    output = tf.nn.relu(batch_norm(conv2d(output, W_conv5_3) + b_conv5_3))
    #output = max_pool(output, 2, 2)

    # output = tf.contrib.layers.flatten(output)
    output = tf.reshape(output, [-1, 512])


    W_fc1 = tf.get_variable('fc1', shape=[512, 1024], initializer=tf.contrib.keras.initializers.he_normal())
    b_fc1 = bias_variable([1024])
    output = tf.nn.relu(batch_norm(tf.matmul(output, W_fc1) + b_fc1) )
    output = tf.nn.dropout(output, keep_prob)


    W_fc2 = tf.get_variable('fc7', shape=[1024, 1024], initializer=tf.contrib.keras.initializers.he_normal())
    b_fc2 = bias_variable([1024])
    output = tf.nn.relu(batch_norm(tf.matmul(output, W_fc2) + b_fc2))
    output = tf.nn.dropout(output, keep_prob)


    W_fc3 = tf.get_variable('fc3', shape=[1024, 1], initializer=tf.contrib.keras.initializers.he_normal())
    b_fc3 = bias_variable([1])
    output = tf.nn.relu(batch_norm(tf.matmul(output, W_fc3) + b_fc3))

    pred = output

    # output  = tf.reshape(output,[-1,10])


    mse_lose = tf.reduce_mean(tf.square(pred - y_))
    train_step = tf.train.MomentumOptimizer(learning_rate, momentum_rate, use_nesterov=True, name="mse_train").minimize(mse_lose)

    #train_step = tf.train.AdamOptimizer(learning_rate, 0.9, 0.99, 1e-08, name="mse_train").minimize(mse_lose)




    # loss function: cross_entropy
    # train_step: training operation
    # cross_entropy = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels=y_, logits=output), name="cross_entropy")
    # l2 = tf.add_n([tf.nn.l2_loss(var) for var in tf.trainable_variables()])
    # train_step = tf.train.MomentumOptimizer(learning_rate, momentum_rate, use_nesterov=True).\
    #     minimize(cross_entropy + l2 * weight_decay)


    # correct_prediction = output.values()[0]
    # accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32), name="accuracy")


    # initial an saver to save model
    saver = tf.train.Saver()


    with tf.Session() as sess:


        sess.run(tf.global_variables_initializer())
        summary_writer = tf.summary.FileWriter(log_save_path,sess.graph)


        # epoch = 164
        # make sure [bath_size * iteration = data_set_number]


        for ep in range(1, total_epoch+1):

            time_start = time.time()

            lr = learning_rate_schedule(ep)
            pre_index = 0
            train_loss = 0.0
            start_time = time.time()


            print("\n epoch %d/%d:" % (ep, total_epoch))


            for it in range(1, iterations+1):
                batch_x = train_x[pre_index:pre_index+batch_size]
                batch_y = train_y[pre_index:pre_index+batch_size]

                # print batch_x.shape, batch_y.shape


                _, batch_loss, prob = sess.run([train_step, mse_lose, pred],
                                         feed_dict={x: batch_x, y_: batch_y, keep_prob: dropout_rate,
                                                    learning_rate: lr, train_flag: True})

                # print "prob", prob, batch_y

                train_loss += batch_loss
                pre_index += batch_size

                print("iteration: %d/%d, train_loss: %.4f"
                      % (it, iterations, train_loss / it))
                # if it == iterations:
                #     train_loss /= iterations
                #
                #     loss_ = sess.run(mse_lose, feed_dict={x: batch_x, y_: batch_y, keep_prob: 1.0, train_flag: True})
                #     train_summary = tf.Summary(value=[tf.Summary.Value(tag="train_loss", simple_value=train_loss)])
                #
                #
                #     val_loss, test_summary = run_testing(sess, ep)
                #
                #
                #     summary_writer.add_summary(train_summary, ep)
                #     summary_writer.add_summary(test_summary, ep)
                #     summary_writer.flush()
                #
                #
                #     print("iteration: %d/%d, cost_time: %ds, train_loss: %.4f, "
                #           "test_loss: %.4f"
                #           % (it, iterations, int(time.time()-start_time), train_loss, val_loss))
                # else:
                #     print("iteration: %d/%d, train_loss: %.4f"
                #           % (it, iterations, train_loss / it))

            time_end = time.time()
            print "time cost: %d s" % (time_end - time_start)


        save_path = saver.save(sess, model_save_path)
        print("Model saved in file: %s" % save_path)