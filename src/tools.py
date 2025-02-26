from PIL import Image, ImageDraw
import numpy as np
import pytesseract

min_region_size=150

def find_abcd_regions(image_path, lower_bound, upper_bound, crop_coords=(100, 200, 400, 700), save_path=None):
    # 载入图片并裁剪
    img = Image.open(image_path)
    img_cropped = img.crop(crop_coords)  # 获取裁剪后的图片
    
    # 转换为RGB并获取像素数据
    img_rgb = img_cropped.convert("RGB")
    pixels = img_rgb.load()

    # 找到符合颜色范围的所有像素点
    color_pixels = []
    for i in range(img_rgb.width):
        for j in range(img_rgb.height):
            r, g, b = img_rgb.getpixel((i, j))
            if (lower_bound[0] <= r <= upper_bound[0] and
                lower_bound[1] <= g <= upper_bound[1] and
                lower_bound[2] <= b <= upper_bound[2]):
                color_pixels.append((i, j))

    # 进行区域合并（Flood Fill）
    def flood_fill(pixels, start_x, start_y, img_rgb, visited):
        to_visit = [(start_x, start_y)]
        region = []
        while to_visit:
            x, y = to_visit.pop()
            if (x, y) not in visited:
                visited.add((x, y))
                region.append((x, y))

                # 检查周围4个方向的相邻像素
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < img_rgb.width and 0 <= ny < img_rgb.height:
                        if (nx, ny) in pixels and (nx, ny) not in visited:
                            to_visit.append((nx, ny))
        return region

    # 初始化标记访问的集合
    visited = set()
    regions = []

    # 查找区域
    for x, y in color_pixels:
        if (x, y) not in visited:
            region = flood_fill(color_pixels, x, y, img_rgb, visited)
            regions.append(region)

    # 过滤出区域大小满足条件的区域
    matching_regions = []

    for region in regions:
        if len(region) >= min_region_size:
            # 获取区域的最小矩形框
            min_x = min(region, key=lambda p: p[0])[0]
            max_x = max(region, key=lambda p: p[0])[0]
            min_y = min(region, key=lambda p: p[1])[1]
            max_y = max(region, key=lambda p: p[1])[1]

            # 返回右上角和右下角的坐标，转换回原图坐标
            matching_regions.append(((max_x + crop_coords[0], min_y + crop_coords[1]), 
                                     (max_x + crop_coords[0], max_y + crop_coords[1])))

    # 如果需要，绘制矩形框并保存
    if save_path:
        draw = ImageDraw.Draw(img)
        for region in matching_regions:
            (top_right, bottom_left) = region
            draw.rectangle([top_right, bottom_left], outline="red", width=2)

        img.save(save_path)

    return matching_regions

def extract_text_from_region(img, top_left, bottom_right, custom_config=r"--psm 3 --oem 3 -l chi_sim+eng"):
    """
    从指定区域提取文本，优化识别效果。

    :param img: PIL 图像对象
    :param top_left: 区域左上角坐标
    :param bottom_right: 区域右下角坐标
    :param custom_config: Tesseract OCR 配置参数
    :return: 提取到的文本
    """
    # 从原图中裁剪出目标区域
    region = img.crop((top_left[0], top_left[1], bottom_right[0], bottom_right[1]))

    # 使用Tesseract进行OCR识别
    text = pytesseract.image_to_string(region, config=custom_config)

    # 返回去除前后空格的文本
    return text.strip()

def generate_text_dict(image_path, coordinates, save_path=None):
    """
    根据坐标生成字典并识别文本内容，并在图中标注区域
    
    :param image_path: 图片路径
    :param coordinates: 区域坐标的列表，每个元素是((x1, y1), (x2, y2))形式的元组
    :param save_path: 保存标注后的图片路径
    :return: 包含区域和文本结果的字典
    """
    # 载入图片
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)
    
    # 定义区域的标签
    labels = ['A', 'B', 'C', 'D']
    
    # 生成字典并提取文本
    text_dict = {}
    for label, (top_left, bottom_right) in zip(labels, coordinates):
        # 转换回原图坐标
        top_left = (top_left[0] + 20, top_left[1])
        bottom_right = (bottom_right[0] + 600, bottom_right[1])
        
        # 提取文本
        text = extract_text_from_region(img, top_left, bottom_right, custom_config=r"--psm 6 -l chi_sim+eng")
        text_dict[label] = text
        
        # 标注区域
        draw.rectangle([top_left, bottom_right], outline="blue", width=2)
        draw.text(top_left, label, fill="blue")
    
    # 保存标注后的图片
    if save_path:
        img.save(save_path)
    
    return text_dict

def generate_quiz(image_path, crop_coords=(100, 200, 400, 650), save_path=None):
    # 载入图片并裁剪
    img = Image.open(image_path)
    
    quiz = extract_text_from_region(img, (crop_coords[0], crop_coords[1]), (crop_coords[2], crop_coords[3]))

    # 保存标注后的图片
    if save_path:
        draw = ImageDraw.Draw(img)
        draw.rectangle([crop_coords[0], crop_coords[1], crop_coords[2], crop_coords[3]], outline="red", width=2)
        img.save(save_path)

    return quiz

