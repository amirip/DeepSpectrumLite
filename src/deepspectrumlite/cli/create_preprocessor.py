#                               DeepSpectrumLite
# ==============================================================================
# Copyright (C) 2020-2021 Shahin Amiriparian, Tobias Hübner, Maurice Gerczuk,
# Sandra Ottl, Björn Schuller: University of Augsburg. All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
# ==============================================================================

'''
This script converts a h5 file to a tflite file
'''
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # print only error messages
import sys
import tensorflow as tf
from tensorflow import keras
import math
from tensorflow.keras import backend as K
from tensorflow.python.saved_model import loader_impl
from deepspectrumlite import HyperParameterList, PreprocessAudio
import time
import numpy as np
import argparse


def print_version():
    print(tf.version.GIT_VERSION, tf.version.VERSION)

if __name__ == "__main__":

    print_version()

    parser = argparse.ArgumentParser()
    parser.add_argument('-hc', '--hyper-config', type=str, dest='hyper_config_file',
                        default='../config/hp_config.json',
                        help='Directory for the hyper parameter config file (default: %(default)s)')
    args = parser.parse_args()

    hyper_parameter_list = HyperParameterList(config_file_name=args.hyper_config_file)
    hparam_values = hyper_parameter_list.get_values(iteration_no=0)
    preprocess = PreprocessAudio(hparams=hparam_values, name="dsl_audio_preprocessor")
    input = tf.convert_to_tensor(np.array(np.random.random_sample((1, 16000)), dtype=np.float32), dtype=tf.float32)
    result = preprocess.preprocess(input)
    # print(result)
    # sys.exit()
    # ATTENTION: antialias is not supported in tflite
    tf.saved_model.save(preprocess, 'preprocessor')

    # new_model = preprocess

    converter = tf.lite.TFLiteConverter.from_saved_model(saved_model_dir='preprocessor')
    converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS,
                                           tf.lite.OpsSet.SELECT_TF_OPS]
    converter.experimental_new_converter = True
    tflite_quant_model = converter.convert()
    open("preprocessor_model.tflite", "wb").write(tflite_quant_model)

    interpreter = tf.lite.Interpreter(model_path="preprocessor_model.tflite")
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    print(input_details)
    print(output_details)

    interpreter.allocate_tensors()

    interpreter.set_tensor(input_details[0]['index'], tf.convert_to_tensor(np.array(np.random.random_sample((1, 16000)), dtype=np.float32), dtype=tf.float32))

    interpreter.invoke()

    output = interpreter.get_tensor(output_details[0]['index'])

    # Test model on random input data.
    input_shape = input_details[0]['shape']
    print("input shape: ", input_shape)
    print("output shape: ", output_details[0]['shape'])
    input_data = np.array(np.random.random_sample(input_shape), dtype=np.float32)
    interpreter.set_tensor(input_details[0]['index'], input_data)
    start_time = time.time()
    interpreter.invoke()
    stop_time = time.time()
    output_data = interpreter.get_tensor(output_details[0]['index'])

    print(output_data)
    print('time: {:.3f}ms'.format((stop_time - start_time) * 1000))



