import argparse
import json
import os

from transformers import AutoTokenizer, AutoModelForCausalLM, TrainerCallback, TrainingArguments, Trainer, \
    DataCollatorForLanguageModeling
import valohai
from accelerate import Accelerator, FullyShardedDataParallelPlugin
from datasets import load_dataset
from peft import LoraConfig, get_peft_model
from torch.distributed.fsdp.fully_sharded_data_parallel import FullOptimStateDictConfig, FullStateDictConfig

from helper import get_run_identification


class FineTuner:
    def __init__(self, args):
        self.data = args.data                                          # 数据集
        self.base_model = args.base_model                                    # 模型名称
        self.output_dir = args.output_dir                                    # 输出文件路径
        self.model_max_length = args.model_max_length                        # 模型最大上下文
        self.warmup_steps = args.warmup_steps                                # 学习率预热
        self.max_steps = args.max_steps                                      # 最大训练步数
        self.learning_rate = args.learning_rate                              # 学习率

        self.setup_accelerator()
        self.setup_model()
        self.setup_datasets()
        self.apply_peft()

    def setup_accelerator(self):
        #
        os.environ['WANDB_DISABLED'] = 'true'

        # user FSDP plugin with loading deepspeed config
        fsdp_plugin = FullyShardedDataParallelPlugin(
            state_dict_config=FullStateDictConfig(offload_to_cpu=True, rank0_only=True),
            optim_state_dict_config=FullOptimStateDictConfig(offload_to_cpu=True, rank0_only=True),
        )
        # create accelerator
        self.accelerator = Accelerator(fsdp_plugin=fsdp_plugin)

    def setup_model(self):

        base_model_id = self.base_model
        # load model with BF16
        self.model = AutoModelForCausalLM.from_pretrained(
            base_model_id,
            # torch_dtype=torch.bfloat16
        )

        # load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            base_model_id,
            model_max_length=self.model_max_length,
            padding_side='right',
            add_eos_token=True,
        )
        # Set the pad equal to the eos to
        # ensure data consistency and reduce the impact of pad information.
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.model.gradient_checkpointing_enable()

    def setup_datasets(self):
        data = self.data

        df = load_dataset("json", data_files=data)
        split_data = df['train'].train_test_split(test_size=0.2)

        def generate_and_tokenize_prompt(prompt):
            return self.tokenizer(formatting_func(prompt))

        def formatting_func(example):
            # text = f"### Question: {example['input']}\n ### Answer: {example['output']}"
            alpaca_prompt = """Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

                    ### Instruction:
                    {}

                    ### Input:
                    {}

                    ### Response:
                    {}"""
            instructions = example["Instruction"]
            inputs = example["Input"]
            outputs = example["Output"]
            text = alpaca_prompt.format(instructions, inputs, outputs) +  self.tokenizer.eos_token
            return text

        self.train_df = split_data['train'].map(generate_and_tokenize_prompt)
        self.val_df = split_data['test'].map(generate_and_tokenize_prompt)



    def print_trainable_parameters(self):
        """
        Prints the number of trainable parameters in the model.
        """
        trainable_params = 0
        all_param = 0
        for _, param in self.model.named_parameters():
            all_param += param.numel()
            if param.requires_grad:
                trainable_params += param.numel()
        print(
            f'trainable params: {trainable_params} || all params: {all_param} || trainable%: {100 * trainable_params / all_param}',
        )

    def apply_peft(self):

        config = LoraConfig(
            r=8,
            lora_alpha=16,
            target_modules=[
                'q_proj',
                'k_proj',
                'v_proj',
                'o_proj',
                'gate_proj',
                'up_proj',
                'down_proj',
                'lm_head',
            ],
            bias='none',
            lora_dropout=0.05,
            task_type='CAUSAL_LM',
        )

        model = get_peft_model(self.model, config)

        self.print_trainable_parameters()

        self.model = self.accelerator.prepare_model(model)

    def train(self):
        checkpoint_output_dir = valohai.outputs().path(self.output_dir)
        trainer = Trainer(
            model=self.model,
            train_dataset=self.train_df,
            eval_dataset=self.val_df,
            args=TrainingArguments(
                output_dir=self.output_dir,
                warmup_steps=self.warmup_steps,
                per_device_train_batch_size=2,
                gradient_accumulation_steps=4,
                max_steps=self.max_steps,
                learning_rate=self.learning_rate,
                logging_steps=10,
                bf16=True,
                tf32=False,
                logging_dir='./logs',
                save_strategy='steps',
                save_steps=10,
                evaluation_strategy='steps',
                eval_steps=17,
                report_to=None,
            ),
            data_collator=DataCollatorForLanguageModeling(self.tokenizer, mlm=False),
            callbacks=[PrinterCallback],
        )

        self.model.config.use_cache = False

        trainer.train()
        model_save_dir = os.path.join(checkpoint_output_dir, 'best_model')

        trainer.save_model(model_save_dir)

        # save metadata
        self.save_valohai_metadata(model_save_dir)

    @staticmethod
    def save_valohai_metadata(save_dir):
        project_name, exec_id = get_run_identification()

        metadata = {
            'valohai.dataset-versions': [
                {
                    'uri': f'dataset://mistral-models/{project_name}_{exec_id}',
                    'targeting_aliases': ['best_mistral_checkpoint'],
                    'valohai.tags': ['dev', 'mistral'],
                },
            ],
        }
        for file in os.listdir(save_dir):
            md_path = os.path.join(save_dir, f'{file}.metadata.json')
            metadata_path = valohai.outputs().path(md_path)
            with open(metadata_path, 'w') as outfile:
                json.dump(metadata, outfile)


class PrinterCallback(TrainerCallback):
    def on_log(self, args, state, control, logs=None, **kwargs):
        _ = logs.pop('total_flos', None)
        print(json.dumps(logs))


def main():
    parser = argparse.ArgumentParser(description='Fine-tune a model')

    # Add arguments based on your script's needs
    # fmt: off
    parser.add_argument("--base_model", type=str, default="mistralai/Mistral-7B-v0.1", help="Base mistral from hugging face")
    parser.add_argument("--data", type=str,
                        default=r"C:\Users\AI\Desktop\data\summarize_abstract_dataset.json", help="Path to the "
                                                                                                  "training data")
    parser.add_argument("--output_dir", type=str, default="finetuned_mistral", help="Output directory for checkpoints")
    parser.add_argument("--model_max_length", type=int, default=8192, help="Maximum length for the model")
    parser.add_argument("--warmup_steps", type=int, default=5, help="Warmup steps")
    parser.add_argument("--max_steps", type=int, default=10, help="Maximum training steps")
    parser.add_argument("--learning_rate", type=float, default=2.5e-5, help="Learning rate")
    # fmt: on

    args = parser.parse_args()

    fine_tuner = FineTuner(args)
    fine_tuner.train()


if __name__ == '__main__':
    # df = load_dataset('json', data_files=dataset)
    main()
    # import torch
    # print(torch.__version__)
    # print(torch.version.cuda)
