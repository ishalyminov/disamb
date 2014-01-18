import codecs
import xml.sax
import sys


class RuscorporaToPlaintextHandler(xml.sax.handler.ContentHandler):
    def __init__(self, in_tagger_type, outfile):
        self.word_features = self.__get_empty_word_feature_map()
        self.out = outfile
        self.within_sentence = False
        self.within_word = False

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
        self.out.write(self.word_features['form'][0])
        for gramm in self.word_features['gramm']:
            self.out.write('_' + gramm)
        self.out.write(' ')

    def characters(self, content):
        if self.within_word:
            self.word_features['form'].append(content.replace('`', ''))
        elif self.within_sentence:
            content = content.strip()
            if content:
                self.out.write(' %s_%s ' % (content, content))

    def ignorableWhitespace(self, content):
        pass

def convert(in_file):
    out = codecs.getwriter('utf-8')(sys.stdout, 'xmlcharrefreplace')
    retcode = 0
    try:
        tagger_handler = RuscorporaToPlaintextHandler(out)
        parser = xml.sax.make_parser()
        parser.setContentHandler(tagger_handler)
        parser.parse(in_file)
    except xml.sax.SAXException:
        retcode = 1
    return retcode

def main():
    if len(sys.argv) < 2:
        usage_string = 'Usage: ruscorpora2plaintext.py <file>'
        print usage_string
        exit(0)
    retcode = convert(sys.argv[1])
    return retcode


if __name__ == '__main__':
    retcode = main()
    exit(retcode)
