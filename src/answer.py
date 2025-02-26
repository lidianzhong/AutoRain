import numpy as np
from PIL import Image, ImageDraw
from .tools import find_abcd_regions, generate_text_dict, generate_quiz

# 固定的参数保存在此文件中
ABCD_PARAMS = {
    "lower_bound": np.array([110, 110, 110]),
    "upper_bound": np.array([160, 160, 160]),
    "crop_coords": (100, 200, 400, 650),
    "save_path": "./data/screenshots/abcd_image.png",
    "text_save_path": "./data/screenshots/abcd_text_image.png"
}

QUIZ_PARAMS = {
    "crop_coords": None,  # 用于动态设置
    "save_path": "./data/screenshots/quiz_image.png"
}

def process_image(image_path):
    """
    处理图片，找到选项区域和题目区域，并提取文本。
    
    :param image_path: 图片路径
    :return: abcd_dict（选项字典） 和 quiz_text（题目文本）
    """
    # 生成选项区域坐标
    abcd_coords = find_abcd_regions(
        image_path,
        lower_bound=ABCD_PARAMS["lower_bound"],
        upper_bound=ABCD_PARAMS["upper_bound"],
        crop_coords=ABCD_PARAMS["crop_coords"],
        save_path=ABCD_PARAMS["save_path"]
    )

    # 动态设置题目区域的裁剪坐标（假设第一块区域的纵坐标作为题目区域下限）
    try:
        quiz_crop_coords = (50, 200, 1200, abcd_coords[0][0][1])
    except IndexError:
        quiz_crop_coords = (50, 200, 1200, 400)
    QUIZ_PARAMS["crop_coords"] = quiz_crop_coords

    # 生成选项
    abcd_dict = generate_text_dict(image_path, abcd_coords, ABCD_PARAMS["text_save_path"])

    # 生成题目
    quiz_text = generate_quiz(image_path, quiz_crop_coords, QUIZ_PARAMS["save_path"])

    return quiz_text, abcd_dict


if __name__ == "__main__":
    # 示例调用
    image_path = "./data/screenshots/image1.png"
    abcd_dict, quiz_text = process_image(image_path)
    print(abcd_dict, quiz_text)