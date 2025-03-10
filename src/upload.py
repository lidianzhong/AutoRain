import requests

def upload_image(file_path):
    # API 接口地址
    api_url = "https://sm.ms/api/v2/upload"
    api_token = "ixM0QXZmIk28gnks34u32P7zOYEQ0dAU"

    headers = {
         "Authorization": api_token,
    }
    files = {
        "smfile": open(file_path, "rb")
    }

    response = requests.post(api_url, headers=headers, files=files)
    result = response.json()

    if result["success"]:
        return result["data"]["url"]
    
    raise ValueError

if __name__ == "__main__":
    # Example usage
    image_path = 'data/login_page.png'
    print(upload_image(image_path))
