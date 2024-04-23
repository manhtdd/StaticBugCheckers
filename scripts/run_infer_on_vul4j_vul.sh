#!/bin/bash

echo ">>> Running Infer" 
python3 python/RunInfer.py \
    -dataset /vul4j/dataset/vul4j_dataset.csv \
    -infer /StaticBugCheckers/static-checkers/infer-linux64-v1.1.0/lib/infer/infer/bin/infer \
    -checkout /tmp/vul4j/vul \
    -result outputs/results.csv