import json
import os
from pathlib import Path

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
        api_key=os.getenv("KIMI_API_KEY"),
        base_url=os.getenv("KIMI_BASE_URL"),
    )

file_list = client.files.list()
for file in file_list.data:
    print(file.filename, file.id)

# client.files.delete(file_id="cocfp71hmfr6003led70")