OUTPUT_DIR=output

mkdir -p $OUTPUT_DIR

function run_analysis {
    XADDR=$1
    XNAME=$2
    XSOURCE=$3
    XTESTFILE=$4
    XRUN=$5
    echo ""
    echo "Run Analysis:"
    echo "ADDR: $XADDR"
    echo "NAME: $XNAME"
    echo "SOLFILEPATH: $XSOURCE"
    echo "TESTFILE $XTESTFILE"
    echo "#TOTAL RUN $XRUN"
    rm -rf $OUTPUT_DIR/$XADDR_error.log
    rm -rf $OUTPUT_DIR/$XADDR.log
    for i in $(eval echo {1..$XRUN})
    do
        echo "Step: $i - $NAME"
        echo "Start: $(date)"
        python3 run.py -s $XSOURCE -c $XNAME -t $XTESTFILE -o $OUTPUT_DIR/$XADDR 2>> $OUTPUT_DIR/$XADDR_error.log >> $OUTPUT_DIR/$XADDR.log
        tar -zcvf $OUTPUT_DIR/$XADDR.tar.gz $OUTPUT_DIR/$XADDR
        rm -rf $OUTPUT_DIR/$XADDR
        echo "End: $(date)"
    done
}

if [ "$#" -ne 3 ]; then
    echo "Illegal number of parameters"
    echo "Correct usage:"
    echo "bash run_test_k_times.sh <input-folder> <test-path.js> <number-of-runs>"
    exit
fi

DIR=$1/*
for SOLFILEPATH in $DIR; do
    regexp="([a-zA-Z0-9]+)-(.+)\\."
    if [[ $SOLFILEPATH =~ $regexp ]]; then
            ADDR="${BASH_REMATCH[1]}"
            NAME="${BASH_REMATCH[2]}"
            TESTPATH=$2
            MAXRUN=$3
            run_analysis $ADDR $NAME $SOLFILEPATH $TESTPATH $MAXRUN
            OUTPUT_I1=$(grep I1 ${OUTPUT_DIR}/${ADDR}.log  | wc -l)
            OUTPUT_I2=$(grep I2 ${OUTPUT_DIR}/${ADDR}.log  | wc -l)
            OUTPUT_I6=$(grep I6 ${OUTPUT_DIR}/${ADDR}.log  | wc -l)
            OUTPUT_I7=$(grep I7 ${OUTPUT_DIR}/${ADDR}.log  | wc -l)
            OUTPUT_I8=$(grep I8 ${OUTPUT_DIR}/${ADDR}.log  | wc -l)
            OUTPUT_I9=$(grep I9 ${OUTPUT_DIR}/${ADDR}.log  | wc -l)
            echo "$NAME"
            echo "OUTPUT_I1 $OUTPUT_I1"
            echo "OUTPUT_I2 $OUTPUT_I2"
            echo "OUTPUT_I6 $OUTPUT_I6"
            echo "OUTPUT_I7 $OUTPUT_I7"
            echo "OUTPUT_I8 $OUTPUT_I8"
            echo "OUTPUT_I9 $OUTPUT_I9"
   fi
done
