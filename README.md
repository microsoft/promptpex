# Project

## Getting Started 

> Use CodeSpaces / dev container to get a fully configured environment.

### Navigating the CLI

* `automatic_pipeline.py` is the main driver  
* It takes input as a prompt using `-i unix/path`  
* If the input file was `foo.txt` and you want to store the output in result dir, do the following:
```sh
python3 automatic_pipeline.py -i foo.txt -o result
```
It automatically creates the dir result/foo to save the result 
* All paths provided to CLI must be unix path, `this/is/a/unix/path` and `\not\this`
* The most common use case is to run the whole pipeline, gen rules, tests and run tests:
```sh
python3 automatic_pipeline.py -i foo.txt -o result --run-tests
```
* To generate rules and exit, use `--gen-rules` and `--gen-tests` for generating tests and existing
* Gen rules `--gen-rules`, Gen tests `--gen-tests` and Run tests `--run-tests`
* `--use-existing-*` will use the old artifacts (rules and tests)
```sh
python3 automatic_pipeline.py -i foo.txt -o result --run-tests --use-existing-rules --use-existing-tests
```
This will run the existing tests without generating new rules and tests
```sh
python3 automatic_pipeline.py -i foo.txt -o result --gen-tests --use-existing-rules
```
This will generate new tests using the old rules.

### Host PromptPex locally

Get the packages by doing `pip install -r requirements.txt`  
OpenAI keys and endpoint needs to be set by setting value of AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT in .env file 

```sh
$ cat .env
$ AZURE_OPENAI_API_KEY="your_key"
$ AZURE_OPENAI_ENDPOINT="api endpoint"
```

#### Extra setup to use local model 
```sh
curl -fsSL https://ollama.com/install.sh | sh
export OLLAMA_HOST="127.0.0.1:8502"
```

Only pull the model you want to run, these can fill up storage pretty quickly
```sh
# ollama pull mistral:latest 
# ollama pull gemma2:9b 
# ollama pull gemma2:2b 
# ollama pull llama3.1:8b 
# ollama pull phi3:medium 
# ollama pull phi3:mini 
# ollama pull gemma2:latest 
# ollama pull llama3.1:latest 
# ollama pull phi3:latest 
# ollama pull phi3:medium-128k
```

```sh
ollama serve & 
```

```sh
cd promptpex/app
python -m streamlit run .\main.py
```

`automatic_pipeline.py` implements the end to end automated prompt fixing pipeline. It takes a cli argument as the path to the prompt (in unix style, sample/prompt.txt).  
```py
python3 automatic_pipeline.py sample/LinuxTerminal.txt
```
The results goes into ap-results/ where variant-0.txt is the initial prompt with rules-0.txt as initial rules. 

## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft 
trademarks or logos is subject to and must follow 
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.
