from PIL import Image, ImageDraw

def create_icon():
    # 创建一个正方形的图像
    size = (256, 256)
    image = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # 绘制圆形背景
    circle_bbox = (20, 20, size[0]-20, size[1]-20)
    draw.ellipse(circle_bbox, fill='#1E90FF')
    
    # 保存为ICO文件
    image.save('timer.ico', format='ICO')

if __name__ == '__main__':
    create_icon() 