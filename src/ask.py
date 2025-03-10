from openai import OpenAI
import base64
import re

from .config import *


def ask(image_path):
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode("utf-8")

    if not API_KEY:
        raise ValueError("Please add an API_KEY.")
    
    client = OpenAI(
        api_key=API_KEY,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    
    completion = client.chat.completions.create(
        model="qwen-vl-plus",
        messages=[
            {
                "role": "system",
                "content": [{"type": "text", "text": "You are a helpful assistant."}]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{base64_image}"}
                    },
                    {"type": "text", "text": "Output the option that best matches the answer to the question among ABCD. Do not output any other content."}
                ]
            }
        ],
    )

    answer = completion.choices[0].message.content
    match = re.search(r'\b[A-D]\b', answer)
    if match:
        return match.group(0)
    
    return 
