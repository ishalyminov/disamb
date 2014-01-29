if [ $# -lt 2 ]; then
    echo "Usage: train_opennlp.sh <train corpus root> <model filename>";
    return 1;
fi

HUNPOS_TRAIN=../hunpos-1.0-linux/hunpos-train
DATASETS_FOLDER=datasets
INPUT=$1;
OUTPUT=$2;

mkdir -p $DATASETS_FOLDER
python create_datasets.py $INPUT $DATASETS_FOLDER

$HUNPOS_TRAIN hunpos.model < $DATASETS_FOLDER > hunpos.result
python check_accuracy.py hunpos.result $DATASETS_DIR/test.xml
