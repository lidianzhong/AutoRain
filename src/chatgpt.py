import requests
import json
import re

def get_chatgpt_answer_from_dict(quiz_text, abcd_dict):
    """
    通过quiz_text(题目)和abcd_dict(选项字典)来向ChatGPT请求正确的答案。

    :param quiz_text: 题目文本
    :param abcd_dict: 选项字典
    :return: ChatGPT 给出的答案(A, B, C, D)
    """
    # 构建问题描述(prompt)
    choices = "\n".join([f"{key}: {value}" for key, value in abcd_dict.items()])
    question = f"题目：{quiz_text}\n选项：\n{choices}\n\n请从选项中选择正确的答案："

    # 请求数据
    url = "https://api.openai-hk.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "hk-i9gflf10000519389e6d3bfda1a233ad5930fdb9c9674088"
    }
    data = {
        "max_tokens": 1200,
        "model": "gpt-3.5-turbo",
        "temperature": 0.8,
        "top_p": 1,
        "presence_penalty": 1,
        "messages": [
            {
                "role": "system",
                "content": "你的任务是根据问题给出答案。问题的类型是选择题。你认为应该选什么。从ABCD中选出一个最合适的答案输出，不要输出任何其他内容。"
            },
            {
                "role": "user",
                "content": question
            }
        ]
    }

    # 发起请求
    response = requests.post(url, headers=headers, data=json.dumps(data).encode('utf-8'))
    result = response.json()

    # 获取返回的答案
    answer = result['choices'][0]['message']['content'].strip()

    # 从答案中提取字母(单个字母，A, B, C, D)
    match = re.search(r'\b[A-D]\b', answer)
    if match:
        return match.group(0)

    # random guess
    return 'D'

if __name__ == "__main__":

    from .answer import process_image

    # 示例调用
    image_path = "./data/screenshots/image1.png"
    quiz_text, abcd_dict = process_image(image_path)
    print(quiz_text, abcd_dict)

    # 获取并打印ChatGPT返回的答案
    answer = get_chatgpt_answer_from_dict(quiz_text, abcd_dict)
    print(f"正确答案是: {answer}")
