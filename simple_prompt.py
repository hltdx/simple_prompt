#!/usr/bin/env python3

import sys, json, argparse, logging
import boto3
from botocore import UNSIGNED
from botocore.config import Config
from botocore import exceptions


class InvokeModel:

    def __init__(self, region=None, model_id=None, proxy_url=None, system_prompt_file=None, guardrail_id=None, guardrail_version=None, log_file=None):
        self.region = region
        self.model_id = model_id
        self.proxy_url = proxy_url
        self.system_prompt_file = system_prompt_file
        self.guardrail_id = guardrail_id
        self.guardrail_version = guardrail_version
        self.log_file = log_file
        self.__bedrock_client = None
        self.__logger = None
        self.__system_prompt = None

    @property
    def bedrock_client(self):
        if not self.__bedrock_client:
            if self.proxy_url:
                self.__bedrock_client = boto3.client(
                    "bedrock-runtime",
                    region_name=self.region,
                    endpoint_url = self.proxy_url,
                    config=Config(signature_version=UNSIGNED)
                )
            else:
                self.__bedrock_client = boto3.client(
                    "bedrock-runtime",
                    region_name=self.region
                )
        return self.__bedrock_client
    
    @property
    def system_prompt(self):
        if not self.__system_prompt:
            with open(self.system_prompt_file, "r") as f:
                self.__system_prompt = f.read()
        return self.__system_prompt
    
    @property
    def logger(self):
        if self.log_file:
            if not self.__logger:
                logging.basicConfig(
                    filename=self.log_file,
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s'
                )
                self.__logger = logging.getLogger(__name__)
                self.__logger.info("Starting conversation model")
                self.__logger.info(f"Model: {self.model_id}")
                self.__logger.info(f"System prompt: {self.system_prompt}")
                if self.guardrail_id:
                    self.__logger.info(f"Guardrail ID: {self.guardrail_id}")
                    self.__logger.info(f"Guardrail version: {self.guardrail_version}")
                if self.proxy_url:
                    self.__logger.info(f"Proxy URL: {self.proxy_url}")
        return self.__logger

    def prompt(self, input):

        native_request = {
            "max_tokens": 1024, 
            "temperature": 0.5,
            "prompt": f"<s>[INST] {self.system_prompt} [/INST] {input} </s>",
            "top_p": 0.7,
            "top_k": 50,
        }

        request = json.dumps(native_request)

        try:
            if self.guardrail_id:
                response = self.bedrock_client.invoke_model(
                    modelId=self.model_id,
                    guardrailIdentifier=self.guardrail_id,
                    guardrailVersion=self.guardrail_version,
                    body=request
                )
            else:
                response = self.bedrock_client.invoke_model(
                    modelId=self.model_id,
                    body=request
                )
            model_response = json.loads(response["body"].read())["content"][0]["text"]
            if self.logger:
                self.logger.info(f"User prompt: {input}")
                self.logger.info(f"Model response: {model_response}")
        except exceptions.ClientError as e:
            print(f"ClientError: {e}")
            return
        except exceptions.ParamValidationError as e:
            print(f"ParamValidationError: {e}")
            return
        except exceptions.BotoCoreError as e:
            print(f"BotoCoreError: {e}")
            return
        except boto3.exceptions.Boto3Error as e:
            print(f"Boto3Error: {e}")
            return
        return model_response


def main():

    parser = argparse.ArgumentParser(description="Simple prompt")
    parser.add_argument("region", help="AWS region")
    parser.add_argument("model_id", help="Model ID")
    parser.add_argument("system_prompt_file", help="File containing the system prompt")
    parser.add_argument("--proxy_url", help="Proxy URL")
    parser.add_argument("--guardrail_id", help="Guardrail ID")
    parser.add_argument("--guardrail_version", help="Guardrail version")
    parser.add_argument("--log_file", help="Log file to save the conversation")

    args = parser.parse_args()
    if args.guardrail_id and not args.guardrail_version:
        print("Guardrail version is required if guardrail ID is provided.")
        sys.exit(1)
    if not args.proxy_url and not args.guardrail_id:
        print("Proxy URL or guardrail ID is required.")
        sys.exit(1)
    if args.proxy_url and args.guardrail_id:
        print("Both proxy URL and guardrail ID cannot be provided together.")
        sys.exit(1)

    i = InvokeModel(**vars(args))

    print(f"Starting conversation with model {args.model_id}")
    print("Press Ctrl+C to exit")
    
    while True:
        try:
            user_input = None
            while not user_input:
                user_input = input("Prompt: ")
                if not user_input:
                    print("Prompt cannot be empty.\n")
            response = i.prompt(user_input)
            print(f"\nModel response: {response}\n")
        except KeyboardInterrupt:
            print("\nCtrl+C detected. Exiting...")
            sys.exit()

if __name__ == "__main__":
    main()


