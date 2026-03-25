import qrcode
import os

# URL para el empleado
url = "http://192.168.1.39:5000"

# Generar QR
qr = qrcode.QRCode(
    version=1,
    box_size=10,
    border=5)
qr.add_data(url)
qr.make(fit=True)

img = qr.make_image(fill_color="black", back_color="white")
img.save("acceso_sistema_qr.png")

print(f"QR generado para: {url}")
print("Escanea este código con tu teléfono para acceder al sistema")
