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
Calculates parameters and FLOPS of a h5 model

Arguments:
    -d File of .h5 model
'''
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # print only error messages
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
import tensorflow as tf

tf.compat.v1.enable_eager_execution()
tf.config.run_functions_eagerly(True)
import numpy as np
import argparse
import time
import h5py
import sys
from deepspectrumlite import AugmentableModel, ARelu


def print_version():
    print(tf.version.GIT_VERSION, tf.version.VERSION)


def get_detailed_stats(model_h5_path):
    session = tf.compat.v1.Session()
    graph = tf.compat.v1.get_default_graph()

    with graph.as_default():
        with session.as_default():
            new_model = tf.keras.models.load_model(model_h5_path, custom_objects={'AugmentableModel': AugmentableModel,
                                                                                  'ARelu': ARelu}, compile=False)
            run_meta = tf.compat.v1.RunMetadata()
            input_details = new_model.get_config()
            input_shape = input_details['layers'][0]['config']['batch_input_shape']

            _ = session.run(new_model.output, {
                'input_1:0': np.random.normal(size=(1, input_shape[1], input_shape[2], input_shape[3]))},
                            options=tf.compat.v1.RunOptions(trace_level=tf.compat.v1.RunOptions.FULL_TRACE),
                            run_metadata=run_meta)

            # '''
            ProfileOptionBuilder = tf.compat.v1.profiler.ProfileOptionBuilder
            opts = ProfileOptionBuilder(ProfileOptionBuilder.time_and_memory()
                                        ).with_step(0).with_timeline_output('test.json').build()

            tf.compat.v1.profiler.profile(
                tf.compat.v1.get_default_graph(),
                run_meta=run_meta,
                cmd='code',
                options=opts)
            # '''
            # Print to stdout an analysis of the memory usage and the timing information
            # broken down by operation types.
            json_export = tf.compat.v1.profiler.profile(
                tf.compat.v1.get_default_graph(),
                run_meta=run_meta,
                cmd='op',
                options=tf.compat.v1.profiler.ProfileOptionBuilder.time_and_memory())

            text_file = open("profiler.json", "w")
            text_file.write(str(json_export))
            text_file.close()
            # print(json_export)
    tf.compat.v1.reset_default_graph()


if __name__ == "__main__":

    print_version()

    parser = argparse.ArgumentParser()

    parser.add_argument('-d', '--model-dir', type=str, dest='model_dir',
                        default='/Users/tobias/PycharmProjects/liteAudioNets-huawei/LiteAudioNets/cli/converted_model.tflite',
                        help='Directory of model (default: %(default)s)')
    args = parser.parse_args()

    # reset seed values
    np.random.seed(0)
    tf.compat.v1.set_random_seed(0)

    interpreter = tf.lite.Interpreter(model_path=args.model_dir)
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    all_layers_details = interpreter.get_tensor_details()

    interpreter.allocate_tensors()

    f = h5py.File("converted_model_weights_infos.hdf5", "w")
    parameters = 0
    for layer in all_layers_details:
        # to create a group in an hdf5 file
        grp = f.create_group(str(layer['index']))

        # to store layer's metadata in group's metadata
        grp.attrs["name"] = layer['name']
        grp.attrs["shape"] = layer['shape']
        # grp.attrs["dtype"] = all_layers_details[i]['dtype']
        grp.attrs["quantization"] = layer['quantization']
        weights = interpreter.get_tensor(layer['index'])
        # print(weights.size)
        parameters += weights.size
        # to store the weights in a dataset
        grp.create_dataset("weights", data=weights)

    f.close()
    print(parameters)
    sys.exit()

    # interpreter.set_tensor(input_details[0]['index'], tf.convert_to_tensor(np.expand_dims(audio_data, 0), dtype=tf.float32))

    interpreter.invoke()

    output = interpreter.get_tensor(output_details[0]['index'])

    # Test model on random input data.
    input_shape = input_details[0]['shape']
    print("input shape: ", input_shape)
    print("output shape: ", output_details[0]['shape'])
    input_data = np.array(np.random.random_sample(input_shape), dtype=np.float32)
    interpreter.set_tensor(input_details[0]['index'], input_data)
    start_time = time.time()
    time.sleep(10.0)
    print("start")
    while True:
        interpreter.invoke()
    stop_time = time.time()
    output_data = interpreter.get_tensor(output_details[0]['index'])

    print(output_data)
    print('time: {:.3f}ms'.format((stop_time - start_time) * 1000))
