import os
import sys
import create_datasets
import hunpos_wrapper
import ruscorpora2plaintext

DATASETS_FOLDER = 'datasets'

def train_model(in_datasets_folder, out_model_name):
    (train_txt_filename, test_txt_filename) = (os.path.join(in_datasets_folder, 'train.txt'),
                                               os.path.join(in_datasets_folder, 'test.txt'))
    return hunpos_wrapper.train_and_calculate_accuracy(train_txt_filename,
                                                       test_txt_filename,
                                                       out_model_name)

def prepare_datasets(in_texts_root):
    if not os.path.exists(DATASETS_FOLDER):
        os.makedirs(DATASETS_FOLDER)
    create_datasets.split_train_test(in_texts_root, DATASETS_FOLDER)
    (train_filename, test_filename) = (os.path.join(DATASETS_FOLDER, 'train.xml'),
                                       os.path.join(DATASETS_FOLDER, 'test.xml'))
    (train_txt_filename, test_txt_filename) = (os.path.join(DATASETS_FOLDER, 'train.txt'),
                                               os.path.join(DATASETS_FOLDER, 'test.txt'))
    (train_txt, test_txt) = (open(train_txt_filename, 'w'), open(test_txt_filename, 'w'))
    ruscorpora2plaintext.convert(open(train_filename), 'hunpos', train_txt)
    ruscorpora2plaintext.convert(open(test_filename), 'hunpos', test_txt)
    train_txt.close()
    test_txt.close()

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print 'Usage: train_hunpos_model.py <input corpus> <model filename> [--create_datasets]'
        exit(0)
    datasets = sys.argv[1]
    if len(sys.argv) == 4 and sys.argv[3] == '--create_datasets':
        prepare_datasets(sys.argv[1])
        datasets = DATASETS_FOLDER
    print train_model(datasets, sys.argv[2])
