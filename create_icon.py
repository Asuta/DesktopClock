from PIL import Image, ImageDraw, ImageFont
import os

def create_icon():
    # 创建一个 256x256 的图像，使用深蓝色背景
    size = 256
    image = Image.new('RGB', (size, size), '#1E90FF')
    draw = ImageDraw.Draw(image)
    
    # 绘制一个简单的圆形
    margin = 20
    draw.ellipse([margin, margin, size-margin, size-margin], fill='white')
    
    # 在中间绘制文字
    try:
        font = ImageFont.truetype("arial.ttf", 100)
    except:
        font = ImageFont.load_default()
    
    text = "计"
    # 获取文本大小
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    # 计算文本位置使其居中
    x = (size - text_width) // 2
    y = (size - text_height) // 2
    
    # 绘制文字
    draw.text((x, y), text, fill='#1E90FF', font=font)
    
    # 保存为ICO文件
    image.save('icon.ico', format='ICO', sizes=[(256, 256)])

if __name__ == '__main__':
    create_icon() 