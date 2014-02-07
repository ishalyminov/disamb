import codecs
import os
import subprocess
import accuracy

DEFAULT_HUNPOS_FOLDER = os.path.join(os.path.dirname(__file__), 'hunpos-1.0-linux')

class HunposWrapper(object):
    def __init__(self,
                 in_hunpos_train_bin=os.path.join(DEFAULT_HUNPOS_FOLDER, 'hunpos-train'),
                 in_hunpos_tag_bin=os.path.join(DEFAULT_HUNPOS_FOLDER, 'hunpos-tag')):
        self.hunpos_train = in_hunpos_train_bin
        self.hunpos_tag = in_hunpos_tag_bin

    def train(self, in_train_stream, out_model_file_name):
        hunpos = subprocess.Popen((self.hunpos_train, out_model_file_name), stdin=in_train_stream)
        hunpos.communicate()

    def tag(self, in_test_stream, in_model_file_name):
        hunpos = subprocess.Popen((self.hunpos_tag, in_model_file_name),
                                  stdin=in_test_stream,
                                  stdout=subprocess.PIPE)
        return hunpos.communicate()[0]

def train_and_calculate_accuracy(in_train_filename, in_test_filename, out_model_name):
    hunpos_wrapper = HunposWrapper('hunpos-1.0-linux/hunpos-train',
                                   'hunpos-1.0-linux/hunpos-tag')
    hunpos_wrapper.train(codecs.getreader('utf-8')(open(in_train_filename)), out_model_name)
    test_tokens = [line.strip().split('\t')[0] for line in open(in_test_filename)]
    open('test.tmp', 'w').write('\n'.join(test_tokens))

    output = hunpos_wrapper.tag(codecs.getreader('utf-8')(open('test.tmp')), out_model_name)
    output_lines = [line.strip() for line in output.split('\n')]
    open('hunpos_result.txt', 'w').write('\n'.join(output_lines))

    test_stream = codecs.getreader('utf-8')(open(in_test_filename))
    gold_stream = codecs.getreader('utf-8')(open('hunpos_result.txt'))
    accuracy_value = accuracy.calculate_accuracy(test_stream, gold_stream)
    return accuracy_value

def tag_file(in_src_filename, in_model_filename, out_dst_filename):
    wrapper = HunposWrapper()
    tagged_text = wrapper.tag(open(in_src_filename), in_model_filename)
    result_file = open(out_dst_filename, 'w')
    print >>result_file, tagged_text