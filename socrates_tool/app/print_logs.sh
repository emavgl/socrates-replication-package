# HOW TO USE
# bash print_logs.sh <input-folder> <output-folder>
DIR=$1
OUTPUT_DIR=$2
for filename in $DIR/*; do
    regexp="([a-zA-Z0-9]+)-(.+)\\."
    if [[ $filename =~ $regexp ]]; then
            ADDR="${BASH_REMATCH[1]}"
            NAME="${BASH_REMATCH[2]}"
            OUTPUT_I1=$(grep I1 ${OUTPUT_DIR}/${ADDR}.log  | wc -l)
            OUTPUT_I2=$(grep I2 ${OUTPUT_DIR}/${ADDR}.log  | wc -l)
            OUTPUT_I6=$(grep I6 ${OUTPUT_DIR}/${ADDR}.log  | wc -l)
            OUTPUT_I7=$(grep I7 ${OUTPUT_DIR}/${ADDR}.log  | wc -l)
            OUTPUT_I8=$(grep I8 ${OUTPUT_DIR}/${ADDR}.log  | wc -l)
            OUTPUT_I9=$(grep I9 ${OUTPUT_DIR}/${ADDR}.log  | wc -l)
            echo "$ADDR,$NAME,$OUTPUT_I1,$OUTPUT_I2,$OUTPUT_I6,$OUTPUT_I7,$OUTPUT_I8,$OUTPUT_I9"
    fi
done
