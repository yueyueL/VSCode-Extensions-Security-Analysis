

output_dir=/PATH/TO/OUTPUT_DIR
data_dir=/PATH/TO/DATA_DIR

python3 run.py \
    --output_dir=$output_dir \
    --model_type=roberta \
    --config_name=microsoft/codebert-base \
    --model_name_or_path=microsoft/codebert-base \
    --tokenizer_name=roberta-base \
    --do_train \
    --train_data_file=$data_dir/train.csv \
    --eval_data_file=$data_dir/eval.csv \
    --test_data_file=$data_dir/test.csv \
    --epoch 5 \
    --block_size 400 \
    --train_batch_size 8 \
    --eval_batch_size 8 \
    --learning_rate 2e-5 \
    --max_grad_norm 1.0 \
    --evaluate_during_training \
    --seed 123456 


# # test
python3 run.py \
    --output_dir=$output_dir \
    --model_type=roberta \
    --config_name=microsoft/codebert-base \
    --model_name_or_path=microsoft/codebert-base \
    --tokenizer_name=roberta-base \
    --do_test \
    --train_data_file=$data_dir/train.csv \
    --eval_data_file=$data_dir/eval.csv \
    --test_data_file=$data_dir/test.csv \
    --eval_batch_size 4 \
    --seed 123456 


# predict
ext_dir=/PATH/TO/EXT_DIR
python3 run.py \
    --output_dir=$output_dir \
    --model_type=roberta \
    --config_name=microsoft/codebert-base \
    --model_name_or_path=microsoft/codebert-base \
    --tokenizer_name=roberta-base \
    --do_detector \
    --train_data_file=$data_dir/train.csv \
    --eval_data_file=$data_dir/eval.csv \
    --test_data_file=$data_dir/test.csv \
    --detector_extention_dir=$ext_dir \
    --eval_batch_size 4 \
    --seed 123456