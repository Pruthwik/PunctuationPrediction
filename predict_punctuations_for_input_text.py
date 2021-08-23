"""Predict punctuations for text, max sentence length=25."""
from argparse import ArgumentParser
import os


def read_text_from_file(file_path):
    """Read text from a file."""
    with open(file_path, 'r', encoding='utf-8') as file_read:
        return file_read.read().strip()


def read_lines_from_file(file_path):
    """Read lines from a file."""
    with open(file_path, 'r', encoding='utf-8') as file_read:
        return file_read.readlines()


def write_lines_into_file(lines, file_path):
    """Write lines into a file."""
    with open(file_path, 'w', encoding='utf-8') as file_write:
        file_write.write('\n'.join(lines) + '\n')


def write_text_into_file(text, file_path):
    """Write text into a file."""
    with open(file_path, 'w', encoding='utf-8') as file_write:
        file_write.write(text + '\n')


def format_text_into_conll(text, max_length=25):
    """Format the input text into conll so that it can be used for crf prediction."""
    tokens_in_text = text.split()
    conll_lines_cased = list()
    conll_lines_lower_cased = list()
    count = 0
    for token in tokens_in_text:
        if count > 0 and count % max_length == 0:
            conll_lines_cased.append('')
            conll_lines_lower_cased.append('')
        conll_lines_lower_cased.append(token.lower())
        conll_lines_cased.append(token)
        count += 1
    return conll_lines_cased, conll_lines_lower_cased


def place_punctuations_in_text(predictions):
    """Place correct punctuations from predictions."""
    punctuated_text = ''
    for prediction in predictions:
        prediction = prediction.strip()
        if prediction:
            token, label = prediction.strip().split()
            if label == '0':
                punctuated_text += token + ' '
            else:
                punctuated_text += token + ' ' + label + ' '
    return punctuated_text.strip()


def main():
    """Pass arguments and call functions here."""
    parser = ArgumentParser()
    parser.add_argument('--input', dest='inp', help='Enter the input file path.')
    parser.add_argument('--model', dest='model', help='Enter the crf model path.')
    parser.add_argument('--output', dest='out', help='Enter the output file path.')
    args = parser.parse_args()
    input_text = read_text_from_file(args.inp)
    input_file_name = args.inp[: args.inp.find('.')]
    conll_lines_cased, conll_lines_lower_cased = format_text_into_conll(input_text)
    write_lines_into_file(conll_lines_lower_cased, input_file_name + '-lower-conll.txt')
    write_lines_into_file(conll_lines_cased, input_file_name + '-conll.txt')
    os.system('crf_test -m ' + args.model + ' ' + input_file_name + '-lower-conll.txt' + ' > ' + input_file_name + '-preds.txt')
    os.system('cut -f2 ' + input_file_name + '-preds.txt > ' + input_file_name + '-only-preds.txt')
    os.system('paste ' + input_file_name + '-conll.txt ' + input_file_name + '-only-preds.txt > ' + input_file_name + '-cased-preds.txt')
    predictions = read_lines_from_file(input_file_name + '-cased-preds.txt')
    punctuated_text = place_punctuations_in_text(predictions)
    if punctuated_text[-1] != '.':
        punctuated_text += ' .'
    write_text_into_file(punctuated_text, args.out)
    os.system('rm -rf ' + input_file_name + '*-conll.txt' + ' ' + input_file_name + '*-preds.txt')


if __name__ == '__main__':
    main()
