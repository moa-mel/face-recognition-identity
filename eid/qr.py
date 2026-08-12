import qrcode

def generate_qr(user_id):
    """
    Generate a QR code for the given user ID.
    """
    data = str(user_id)
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)

    return qr.make_image()