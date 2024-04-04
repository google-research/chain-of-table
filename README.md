# Chain of Table

Code for paper [Chain-of-Table: Evolving Tables in the Reasoning Chain for Table Understanding](https://arxiv.org/abs/2401.04398)

## Environment

```shell
conda create --name cotable python=3.10 -y
conda activate cotable
pip install -r requirements.txt 
```

## Command Usages

### Arguments

- `--dataset_path`: path to the dataset, default: `./data/tabfact/test.jsonl`
- `--raw2clean_path`: path to the preprocessed raw2clean file, default: `./data/tabfact/raw2clean.json` (cleaned by [Dater](https://arxiv.org/pdf/2301.13808.pdf))
- `--model_name`: name of the OpenAI API, default: `gpt-3.5-turbo-16k-0613`
- `--result_dir`: path to the result directory, default: `./results/tabfact`
- `--openai_key`: key of the OpenAI API
- `--first_n`: number of the first n samples to evaluate, default: `-1` means whole dataset
- `--n_proc`: number of processes to use in multiprocessing, default: `1`
- `--chunk_size`: chunk size used in multiprocessing, default: `1`

### Example usages

1. Run tests on the first 10 cases

   ```shell
   python run_tabfact.py \
   --result_dir 'results/tabfact_first10' \
   --first_n 10 \
   --n_proc 10 \
   --chunk_size 1 \
   --openai_api_key <YOUR_KEY>
   ```

2. Run the experiment on the whole dataset

   ```shell
   python run_tabfact.py \
   --result_dir 'results/tabfact' \
   --n_proc 20 \
   --chunk_size 10 \
   --openai_api_key <YOUR_KEY>
   ```

## Cite

If you find this repository useful, please consider citing:

```bibtex
@article{wang2024chain,
  title={Chain-of-Table: Evolving Tables in the Reasoning Chain for Table Understanding},
  author={Wang, Zilong and Zhang, Hao and Li, Chun-Liang and Eisenschlos, Julian Martin and Perot, Vincent and Wang, Zifeng and Miculicich, Lesly and Fujii, Yasuhisa and Shang, Jingbo and Lee, Chen-Yu and Pfister, Tomas},
  journal={ICLR},
  year={2024}
}
```

## Acknowledgement

We thank [Dater](https://arxiv.org/pdf/2301.13808.pdf) for providing the cleaned TabFact dataset and releasing the [code](https://github.com/AlibabaResearch/DAMO-ConvAI/tree/main/dater). We include the cleaned raw2clean file in the `data/tabfact` directory and the prompts for row/column selection in the `operations/sel_col_row_prompt.py` file under the MIT License.