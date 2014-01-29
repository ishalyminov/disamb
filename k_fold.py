import os
import random
import sys
from sklearn import cross_validation
import create_datasets
import hunpos_wrapper
import ruscorpora2plaintext

FOLDS_NUMBER = 6
DATASETS_FOLDER = 'datasets'

def perform_kfold_cross_validation(in_texts_root):
    if not os.path.isdir(DATASETS_FOLDER):
        os.makedirs(DATASETS_FOLDER)
    sentences_number = create_datasets.get_sentences_number_in_corpus(in_texts_root)
    sentences = range(sentences_number)
    print 'Sentences in the corpus: %d' % sentences_number
    random.seed(271)
    random.shuffle(sentences)
    kfold = cross_validation.KFold(len(sentences), n_folds=FOLDS_NUMBER)
    fold_accuracies = []
    for (train_index, test_index) in kfold:
        (train_filename, test_filename) = (os.path.join(DATASETS_FOLDER, 'train.xml'),
                                           os.path.join(DATASETS_FOLDER, 'test.xml'))
        (train_file, test_file) = (open(train_filename, 'w'),
                                   open(test_filename, 'w'))
        create_datasets.perform_splitting(in_texts_root,
                                          train_index,
                                          test_index,
                                          train_file,
                                          test_file)
        train_file.close()
        test_file.close()
        (train_txt, test_txt) = (open('train.txt', 'w'), open('test.txt', 'w'))
        ruscorpora2plaintext.convert(open(train_filename), 'hunpos', train_txt)
        ruscorpora2plaintext.convert(open(test_filename), 'hunpos', test_txt)
        train_txt.close()
        test_txt.close()
        fold_accuracy = hunpos_wrapper.train_and_calculate_accuracy('train.txt',
                                                                    'test.txt',
                                                                    'hunpos.model')
        fold_accuracies.append(fold_accuracy)
    mean_accuracy = sum(fold_accuracies) / len(fold_accuracies)
    print 'Mean accuracy across %d folds = %.3f' % (FOLDS_NUMBER, mean_accuracy)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Usage: k_fold.py <source texts root folder>'
        exit(0)
    perform_kfold_cross_validation(sys.argv[1])