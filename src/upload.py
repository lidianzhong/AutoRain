import requests

def upload_image(file_path):
    # API 接口地址
    api_url = 'https://imgbed.yiyunt.cn/api/upload/'

    # 打开图片文件
    with open(file_path, 'rb') as f:
        # 创建文件字典
        files = {'fileupload': f}
        
        # 发起 POST 请求
        response = requests.post(api_url, files=files)
        
        # 输出响应结果中的 URL
        return response.json().get('url')

if __name__ == "__main__":
    # Example usage
    image_path = 'data/login_page.png'
    print(upload_image(image_path))
