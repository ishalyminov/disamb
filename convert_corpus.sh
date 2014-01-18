if [ $# -lt 1 ]; then
    echo "Usage: convert_corpus.sh <source text folder>";
    return 1;
fi

INPUT=$1;
find $INPUT -type f -exec python ruscorpora2plaintext.py {} \;
