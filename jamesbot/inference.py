#! /usr/bin/env python3
from __future__ import print_function
import numpy as np
import keras
import json
from keras.models import Model
import os

os.environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"]=""

class NeuralModel:
    def __init__(self, model_config_path):
        with open(model_config_path) as f:
            config = json.load(f)

        self.max_length = config["max_length"]
        self.char_index = config["char_index"]
        self.index_char = dict((i, char) for char, i in self.char_index.items())
        self.decoder = keras.models.load_model(config["decoder_path"])
        self.encoder = keras.models.load_model(config["encoder_path"])
        pass

    def generate_response(self, query):
        if len(query) >= self.max_length-2:
            return None

        query = '\x02'+query+'\x03'
        input_data = np.zeros(
            (1, self.max_length, len(self.char_index)),
            dtype='float32'
        )

        for j, c in enumerate(query):
            input_data[0, j, self.char_index[c]] = 1.

        states_value = self.encoder.predict(input_data)

        target_seq = np.zeros((1, 1, len(self.char_index)))
        target_seq[0, 0, self.char_index['\x02']] = 1.
        
        response = ''

        while True:
            output_chars, h = self.decoder.predict([target_seq, states_value])

            #candidate_indices = np.arange(len(char_index))
            candidate_indices = np.argpartition(output_chars[0, -1, :], -2)[-2:]
            candidate_weights = output_chars[0, -1, candidate_indices]
            candidate_weights /= candidate_weights.sum()

            sampled_index = np.random.choice(candidate_indices, 1, p=candidate_weights)[0]
            sampled_char = self.index_char[sampled_index]

            if sampled_char == '\x03' or len(response) > self.max_length:
                break

            response += sampled_char
            
            target_seq = np.zeros((1, 1, len(self.char_index)))
            target_seq[0, 0, sampled_index] = 1.
            states_value = h

        return response
