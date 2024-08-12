# Project

## Getting Started 

> Use CodeSpaces to get a fully configured environment.

Get the packages by doing `pip install -r requirements.txt`  
OpenAI keys needs to be set the value of AZURE_OPENAI_API_KEY in .env file 

```sh
$ cat .env
$ AZURE_OPENAI_API_KEY="your_key"
```

`automatic_pipeline.py` implements the end to end automated prompt fixing pipeline. It takes a cli argument as the path to the prompt (in unix style, sample/prompt.txt).  
```py
python3 automatic_pipeline.py sample/LinuxTerminal.txt
```
The results goes into ap-results/ where variant-0.txt is the initial prompt with rules-0.txt as initial rules. 

`regression_pipeline.py` implements the end to end regression detection pipeline. It takes a cli argument as the path to the prompt (in unix style, sample/prompt.txt).
```py
python3 regression_pipeline.py
```

`simple_pipeline.py` implements the basic pipeline, change the `input_file` variable on line 8.
```py
python3 simple_pipeline.py
```

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
