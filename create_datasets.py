import codecs
import os
import random
import re
import sys
import xml.sax

TRAIN_SENTENCES_RATIO = 8/10.

class DatasetSplitter(xml.sax.handler.ContentHandler):
    def __init__(self, in_train_file, in_test_file, in_train_indices, in_test_indices):
        self.train_file = in_train_file
        self.test_file = in_test_file
        self.train_indices = in_train_indices
        self.test_indices = in_test_indices
        self.current_output = None
        self.within_sentence = False
        self.sentence_counter = -1
        for out_file in [self.train_file, self.test_file]:
            out_file.write('<?xml version="1.0" encoding="utf-8"?>\n<body>\n')

    def startDocument(self):
        pass

    def endDocument(self):
        pass

    def startElement(self, tag, attrs):
        if tag == 'ana':
            self.flush_tag(tag, attrs)
        if tag == 'w':
            self.flush_tag(tag, attrs)
            self.within_word = True
        if tag == 'se':
            self.within_sentence = True
            self.sentence_counter += 1
            if self.sentence_counter % 1000 == 0:
                print 'Processed %d sentences' % self.sentence_counter
            self.set_output()
            self.flush_tag(tag, attrs)

    def endElement(self, tag):
        if tag == 'se':
            self.within_sentence = False
            self.flush_text('\n')

        if tag in ['se', 'w', 'ana']:
            self.flush_tag('/' + tag)

    def set_output(self):
        if self.sentence_counter in self.train_indices:
            self.current_output = self.train_file
        elif self.sentence_counter in self.test_indices:
            self.current_output = self.test_file
        else:
            exit('%d is neither in test nor in train sentences!')

    def characters(self, content):
        if self.within_sentence:
            content_filtered = re.sub('\s', ' ', content)
            content_filtered = content_filtered.replace('`', '')
            content_filtered = content_filtered.lower()
            self.flush_text(content_filtered)

    def ignorableWhitespace(self, whitespace):
        self.characters(whitespace)

    def flush_tag(self, in_tag_name, in_tag_attrs={}):
        self.current_output.write('<%s' % in_tag_name)
        for (name, value) in in_tag_attrs.items():
            self.current_output.write(' %s="%s"' % (name, value.lower().replace('&', '&amp;')))
        self.current_output.write('>')

    def flush_text(self, in_text):
        text = in_text.replace('>', '&gt;').replace('<', '&lt;').replace('&', '&amp;')
        self.current_output.write(text)

    def close_xmls(self):
        for out_file in [self.train_file, self.test_file]:
            out_file.write('</body>\n')

def get_sentences_number(in_file):
    result = 0
    for line in open(in_file):
        result += len(re.findall('<se.*?>', line))
    return result

def get_sentences_number_in_corpus(in_texts_root):
    sentences_in_corpus_number = 0
    for root, dirs, files in os.walk(in_texts_root, followlinks=True):
        for filename in files:
            sentences_in_corpus_number += get_sentences_number(os.path.join(root, filename))
    return sentences_in_corpus_number

def perform_splitting(in_texts_root, in_train_indices, in_test_indices, out_train, out_test):
    splitter = DatasetSplitter(codecs.getwriter('utf-8')(out_train),
                               codecs.getwriter('utf-8')(out_test),
                               in_train_indices,
                               in_test_indices)
    for root, dirs, files in os.walk(in_texts_root, followlinks=True):
        for filename in files:
            parser = xml.sax.make_parser()
            parser.setContentHandler(splitter)
            parser.parse(os.path.join(root, filename))
    splitter.close_xmls()
    print 'Corpus has been split as %d train and %d test sentences' % \
        (len(in_train_indices), len(in_test_indices))

def split_train_test(in_texts_root, in_result_root):
    if not os.path.isdir(in_result_root):
        os.makedirs(in_result_root)

    (train_filename, test_filename) = (os.path.join(in_result_root, 'train.xml'),
                                       os.path.join(in_result_root, 'test.xml'))
    sentences_number = get_sentences_number_in_corpus(in_texts_root)
    sentences = range(sentences_number)
    print 'Sentences in the corpus: %d' % sentences_number
    random.seed(271)
    random.shuffle(sentences)
    train_sentences = set(sentences[:int(sentences_number * TRAIN_SENTENCES_RATIO)])
    test_sentences = set(sentences[int(sentences_number * TRAIN_SENTENCES_RATIO):])
    (train_file, test_file) = (open(train_filename, 'w'), open(test_filename, 'w'))
    perform_splitting(in_texts_root, train_sentences, test_sentences, train_file, test_file)
    train_file.close()
    test_file.close()


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print 'Usage: create_datasets.py <source texts root folder> <result datasets folder>'
        exit(0)
    split_train_test(sys.argv[1], sys.argv[2])
