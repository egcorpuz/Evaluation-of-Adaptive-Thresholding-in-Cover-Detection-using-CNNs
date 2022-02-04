# modified codes from github repository https://github.com/calmisential/Basic_CNNs_TensorFlow2

from __future__ import absolute_import, division, print_function
import tensorflow as tf
import tensorflow.keras as nn
import math
import argparse

from configuration import IMAGE_HEIGHT, IMAGE_WIDTH, CHANNELS, \
    EPOCHS, BATCH_SIZE, save_model_dir, save_every_n_epoch
from prepare_data import generate_datasets, load_and_preprocess_image
from models import get_model

########### progress bar implementation modules ############
import sys
import time
#############################################################

def print_model_summary(network):
    network.build(input_shape=(None, IMAGE_HEIGHT, IMAGE_WIDTH, CHANNELS))
    network.summary()


def process_features(features, data_augmentation):
    image_raw = features['image_raw'].numpy()
    image_tensor_list = []
    for image in image_raw:
        image_tensor = load_and_preprocess_image(image, data_augmentation=data_augmentation)
        image_tensor_list.append(image_tensor)
    images = tf.stack(image_tensor_list, axis=0)
    labels = features['label'].numpy()

    return images, labels


parser = argparse.ArgumentParser()
parser.add_argument("--idx", default=0, type=int)


if __name__ == '__main__':
    gpus = tf.config.list_physical_devices('GPU')
    print("Num GPUs Available: ", len(gpus)) # omitted originally
    if gpus:
        try:
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
            logical_gpus = tf.config.list_logical_devices('GPU')
            print(len(gpus), "Physical GPUs,", len(logical_gpus), "Logical GPUs")
        except RuntimeError as e:
            print(e)

    args = parser.parse_args()

    # get the dataset
    train_dataset, valid_dataset, test_dataset, train_count, valid_count, test_count = generate_datasets()

    # create model
    model = get_model(args.idx)
    print_model_summary(network=model)

    # define loss and optimizer
    loss_object = tf.keras.losses.SparseCategoricalCrossentropy()
    optimizer = nn.optimizers.Adam(learning_rate=1e-3)

    train_loss = tf.keras.metrics.Mean(name='train_loss')
    train_accuracy = tf.keras.metrics.SparseCategoricalAccuracy(name='train_accuracy')

    valid_loss = tf.keras.metrics.Mean(name='valid_loss')
    valid_accuracy = tf.keras.metrics.SparseCategoricalAccuracy(name='valid_accuracy')

    # @tf.function
    def train_step(image_batch, label_batch):
        with tf.GradientTape() as tape:
            predictions = model(image_batch, training=True)
            loss = loss_object(y_true=label_batch, y_pred=predictions)
        gradients = tape.gradient(loss, model.trainable_variables)
        optimizer.apply_gradients(grads_and_vars=zip(gradients, model.trainable_variables))

        train_loss.update_state(values=loss)
        train_accuracy.update_state(y_true=label_batch, y_pred=predictions)

    # @tf.function
    def valid_step(image_batch, label_batch):
        predictions = model(image_batch, training=False)
        v_loss = loss_object(label_batch, predictions)

        valid_loss.update_state(values=v_loss)
        valid_accuracy.update_state(y_true=label_batch, y_pred=predictions)

    # start training
    ######### print current time ###########
    print("Start time: {}".format(time.strftime("%I:%M:%S %p")))
    ######### print current time ###########
    for epoch in range(EPOCHS):
        step = 0

        #### create the progress bar widget ######
        prefix="Epoch {}/{}: ".format(epoch+1, EPOCHS)
        size=60
        file=sys.stdout
        count = math.ceil(train_count / BATCH_SIZE) # max len of the iterable
        def show(j):
            x = int(size*j/count)
            file.write("%s[%s%s] %i/%i\r" % (prefix, "="*x, "."*(size-x), j, count))
            file.flush()        
        #### create the progress bar widget #######

        for features in train_dataset:
            step += 1
            show(step) # update the progress bar
            images, labels = process_features(features, data_augmentation=True)
            train_step(images, labels)
            # print("Epoch: {}/{}, step: {}/{}, loss: {:.5f}, accuracy: {:.5f}".format(epoch,
            #                                                                          EPOCHS,
            #                                                                          step,
            #                                                                          math.ceil(train_count / BATCH_SIZE),
            #                                                                          train_loss.result().numpy(),
            #                                                                          train_accuracy.result().numpy()))
        file.write("\n") # enter key replaces progress bar
        file.flush() # show # enter key replaces progress bar

        for features in valid_dataset:
            valid_images, valid_labels = process_features(features, data_augmentation=False)
            valid_step(valid_images, valid_labels)

        print("Epoch {}/{} done, Current time: {}, train loss: {:.5f}, train accuracy: {:.5f}, "
              "valid loss: {:.5f}, valid accuracy: {:.5f}".format(epoch+1, EPOCHS,
                                                                    time.strftime("%I:%M:%S %p"), 
                                                                    train_loss.result().numpy(),
                                                                    train_accuracy.result().numpy(),
                                                                    valid_loss.result().numpy(),
                                                                    valid_accuracy.result().numpy()))
        train_loss.reset_states()
        train_accuracy.reset_states()
        valid_loss.reset_states()
        valid_accuracy.reset_states()

        if epoch % save_every_n_epoch == 0:
            model.save_weights(filepath=save_model_dir+"epoch-{}".format(epoch), save_format='tf')


    # save weights
    model.save_weights(filepath=save_model_dir+"ResNet18_NonAdaptive_30k_model", save_format='tf')

    # save the whole model
    tf.keras.models.save_model(model, save_model_dir)
    print("Model saved.") #originally omitted
    
    ######### print current time ###########
    print("End time: {}".format(time.strftime("%I:%M:%S %p")))
    ######### print current time ###########

    # convert to tensorflow lite format
    # model._set_inputs(inputs=tf.random.normal(shape=(1, IMAGE_HEIGHT, IMAGE_WIDTH, CHANNELS)))
    # converter = tf.lite.TFLiteConverter.from_keras_model(model)
    # tflite_model = converter.convert()
    # open("converted_model.tflite", "wb").write(tflite_model)