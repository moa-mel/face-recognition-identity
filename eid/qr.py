import qrcode

def generate_qr(user_id):
    data = str(user_id)
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)

    return qr.make_image()