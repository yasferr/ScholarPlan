import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_key = os.getenv("AZURE_OPENAI_API_KEY")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")

client = OpenAI(
    base_url=endpoint,
    api_key=api_key
)


def ask_llm(prompt):
    response = client.responses.create(
        model=deployment,
        input=prompt
    )

    return response.output_text