import codecs
import xml.sax
import sys

class RuscorporaToPlaintextHandler(xml.sax.handler.ContentHandler):
    def __init__(self, in_tagger_type, outfile):
        self.tagger_type = in_tagger_type
        self.word_features = self.__get_empty_word_feature_map()
        self.out = outfile
        self.within_sentence = False
        self.within_word = False

        self.feature_delimiter = '_'
        self.word_delimiter = ' '
        if self.tagger_type == 'hunpos':
            self.feature_delimiter = '\t'
            self.word_delimiter = '\n'

    def __get_empty_word_feature_map(self):
        return {'form': [], 'lex': [], 'gramm': []}

    def startElement(self, tag, attrs):
        if tag == 'w':
            self.within_word = True
            self.word_features = self.__get_empty_word_feature_map()
        if tag == 'ana':
            self.word_tagged = True
            self.do_not_parse_sentence = True
            self.word_features['lex'].append(attrs['lex'])
            self.word_features['gramm'].append(attrs['gr'])
        if tag == 'se':
            self.within_sentence = True

    def endElement(self, tag):
        if tag == 'se':
            self.within_sentence = False
            self.out.write('\n')
        if tag == 'w':
            self.within_word = False
            self.__flush_word()

    def __flush_word(self):
        if len(self.word_features['lex']) != len(self.word_features['gramm']):
            print self.word_features
            print >>sys.stderr, 'Poor parsing'
            exit(0)
        word_features = [self.word_features['form'][0]] + self.word_features['gramm']
        self.out.write(self.feature_delimiter.join(word_features))
        self.out.write(self.word_delimiter)

    def __flush_punct(self, in_content):
        content_tokens = in_content.strip().split()
        for content_token in content_tokens:
            self.out.write(self.feature_delimiter.join([content_token] * 2))
            self.out.write(self.word_delimiter)

    def characters(self, content):
        if self.within_word:
            self.word_features['form'].append(content.replace('`', ''))
        elif self.within_sentence:
            self.__flush_punct(content)

    def ignorableWhitespace(self, content):
        pass

def convert(in_stream, in_tagger_type, out_stream):
    out = codecs.getwriter('utf-8')(out_stream, 'xmlcharrefreplace')
    retcode = 0
    try:
        tagger_handler = RuscorporaToPlaintextHandler(in_tagger_type, out)
        parser = xml.sax.make_parser()
        parser.setContentHandler(tagger_handler)
        parser.parse(in_stream)
    except xml.sax.SAXException:
        retcode = 1
    return retcode

def main():
    if len(sys.argv) < 3:
        usage_string = 'Usage: ruscorpora2plaintext.py <file> <tagger type: hunpos|opennlp>'
        print usage_string
        exit(0)
    tagger_type = sys.argv[2]
    retcode = convert(open(sys.argv[1]), tagger_type, sys.stdout)
    return retcode


if __name__ == '__main__':
    retcode = main()
    exit(retcode)
