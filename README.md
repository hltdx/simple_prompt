# Simple Prompt
A simple script for sending prompts to Bedrock models. The script supports sending prompts directly to Bedrock with an Amazon Guardrail enabled or by sending prompts to Bedrock through a HiddenLayer LLM Proxy.

## Usage
```shell
simple_prompt.py [-h] [--proxy_url PROXY_URL]
                        [--guardrail_id GUARDRAIL_ID]
                        [--guardrail_version GUARDRAIL_VERSION]
                        [--log_file LOG_FILE]
                        region model_id model_version system_prompt

Simple prompt

positional arguments:
  region                AWS region
  model_id              Model ID
  model_version         Model version
  system_prompt         System prompt

options:
  -h, --help            show this help message and exit
  --proxy_url PROXY_URL
                        Proxy URL
  --guardrail_id GUARDRAIL_ID
                        Guardrail ID
  --guardrail_version GUARDRAIL_VERSION
                        Guardrail version
  --log_file LOG_FILE   Log file to save the conversation
```

### Notes
 - The model_id positional argument must be the inference endpoint of the Bedrock model, e.g. "us.anthropic.claude-3-5-haiku-20241022-v1:0".
 - The model_version positional parameter must be the AWS provided version of the model, e.g. "bedrock-2023-05-31".
 - The --proxy_url parameter needs to be followed by the URL of the LLM Proxy, e.g. --proxy_url "http://internal-xyz-123.<region>.elb.amazonaws.com/"
 - The --guardrail_id parameter needs to be followed by the AWS provided Guardrail ID.
 - If the --proxy_url parameter is set, the --guardrail_id parameter cannot be set and vise versa.
 - If the --log_file parameter is specified, it must be followed by a file name that you would like to write logs to, e.g. --log_file "proxy-prompts.log" or --log_file "guardrail-prompts.log".

## Other Recommendations
Ideally, this script should be run from an EC2 instance that has `bedrock:InvokeModel` and `bedrock:InvokeModelWithResponseStream` privileges for the target model as well as `bedrock:ApplyGuardrail` privileges for the Guardrail to be tested.

The EC2 instance also needs newtork connectivity with the HiddenLayer LLM Proxy.