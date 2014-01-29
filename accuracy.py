import codecs
import sys
import itertools


def check_tags(in_test_tags, in_gold_tags):
    if not len(in_test_tags) or not len(in_gold_tags):
        return False
    # POS tag matching
    if in_test_tags[0] != in_gold_tags[0]:
        return False
    # matching morphological features as sets
    return set(in_test_tags[1:]).issubset(set(in_gold_tags[1:]))

def calculate_accuracy(in_test_answers, in_gold_answers):
    tokens_overall = 0
    tokens_right = 0
    # input file in of the format: FORM \t GRAMMAR
    for (test_line, gold_line, line_number) in zip(in_test_answers, in_gold_answers, itertools.count()):
        test_tokens = filter(None, test_line.strip().split('\t'))
        gold_tokens = filter(None, gold_line.strip().split('\t'))

        if bool(len(test_tokens)) != bool(len(gold_tokens)):
            exit('Inputs unmatched at line %d: "%s" "%s"' % (line_number + 1, test_line, gold_line))
        if not len(test_tokens) and not len(gold_tokens):
            continue
        # forms matching
        if test_tokens[0] != gold_tokens[0]:
            exit('Inputs unmatched at line %d: "%s" "%s"' % (line_number + 1, test_line, gold_line))
        tokens_overall += 1
        tokens_right += check_tags(test_tokens[1].split(','), gold_tokens[1].split(','))
    return tokens_right / float(tokens_overall)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print 'Usage: accuracy.py <test answers file> <gold answers file>'
        exit(0)
    test_stream = codecs.getreader('utf-8')(open(sys.argv[1]))
    gold_stream = codecs.getreader('utf-8')(open(sys.argv[2]))
    accuracy = calculate_accuracy(test_stream, gold_stream)
    print '%.3f' % accuracy
