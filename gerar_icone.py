from PIL import Image 
 
img = Image.new("RGB", (256, 256), (0, 75, 141)) 
img.save("icon.ico", format="ICO", sizes=[(256, 256), (64, 64), (48, 48), (32, 32), (16, 16)]) 
print("icon.ico criado!") 
