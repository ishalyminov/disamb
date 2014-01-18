if [ $# -lt 2 ]; then
    echo "Usage: train_opennlp.sh <train corpus filename> <model filename>";
    return 1;
fi

INPUT=$1;
OUTPUT=$2;

java -Xmx8G -jar lib/opennlp-tools-1.5.3.jar POSTaggerTrainer $INPUT