# EffiBench: Benchmarking the Efficiency of Automatically Generated Code 

##  :round_pushpin: Abstract
Code generation models have increasingly become integral to aiding software development. Although current research has thoroughly examined the correctness of the code produced by code generation models, a vital aspect that plays a pivotal role in green computing and sustainability efforts — the efficiency of the generated code — has often been neglected. This paper presents Effibench, a benchmark with 1,000 efficiency-critical coding problems to assess the efficiency of code generated by code generation models. EffiBench contains a diverse set of LeetCode coding problems. Each problem is paired with an executable human-written canonical solution, which obtains the SOTA efficiency on the LeetCode solution leaderboard. With EffiBench, we empirically examine the ability of 42 large language models (35 open-source and 7 closed-source) to generate efficient code. Our evaluation results demonstrate that the efficiency of the code generated by LLMs is generally worse than the efficiency of human-written canonical solutions. For example, GPT-4 generated code has an average \textbf{3.12} times execution time that of the human-written canonical solutions. In the most extreme cases, the execution time and total memory usage of GPT-4 code are \textbf{13.89} and \textbf{43.92} times that of the canonical solutions. The source code of EffiBench is released on \url{ https://github.com/huangd1999/EffiBench }. We also provide the LeaderBoard in \url{ https://huggingface.co/spaces/EffiBench/effibench-leaderboard }.

## :rocket: Updates
**02/21/2024:** Code released

**04/15/2024:** HuggingFace: [EffiBench](https://huggingface.co/datasets/DONG19/EffiBench)

## Installation

```
git clone git@github.com:huangd1999/EffiBench.git
cd EffiBench
pip install -r requirements.txt
chmod +x ./scripts/run_code.sh
```

## Evaluation on EffiBench
Our evaluation consists of two steps: generation and metrics calculation.


### Generation

#### Open-sourced Models
For open-sourced models like StarCoder, DeepSeek-Coder, etc., we provide batch inference scripts for fast inference on EffiBench. 

```bash
cd src
python open_source_model_completion.py \
  --model codellama/CodeLlama-70b-Instruct-hf 
```

#### OpenAI models
OpenAI models are accessible through an API. You may use the following script:
```bash
cd src
python closed_source_model_completion.py \
  --model gpt-3.5-turbo 
```


### Metrics Calculation
After obtaining the generation, we can calculate the final metrics
```bash
cd src
python code_efficiency_calculator.py \
  --model gpt-3.5-turbo
python report_overhead.py # Please specify evaluation model lists in Line 51. You can evaluate several models (e.g., ["deepseek-coder-1.3b-instruct", "gpt-3.5-turbo"])
```

### Submit Evaluation Request
[filing a request](https://github.com/huangd1999/EffiBench/issues/new?assignees=&labels=model+eval&projects=&template=model_eval_request.yml&title=%F0%9F%92%A1+%5BREQUEST%5D+-+%3CMODEL_NAME%3E) to add your models on our leaderboard!


## Citation

```
@article{huang2024effibench,
  title={EffiBench: Benchmarking the Efficiency of Automatically Generated Code},
  author={Huang, Dong and Shang, Weiyi and Qing, Yuhao and Cui, Heming and Zhang, Jie M},
  journal={arXiv preprint arXiv:2402.02037},
  year={2024}
}
```
## Questions
Please feel free to email us (email addresses in the [paper](https://arxiv.org/pdf/2402.02037)). You may also submit an issue in this repo.


## License

This project is licensed under the Apache-2.0 License.

