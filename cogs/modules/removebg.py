from rembg.bg import remove
from PIL import Image

input_path = 'temp/rembg/b3-i.png'
output_path = 'temp/rembg/b3-o.png'

ip = Image.open(fp=input_path, mode='r').convert()
print(type(ip))
output = remove(ip)
output.save(output_path) 