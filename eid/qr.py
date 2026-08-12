import qrcode

def generate_qr(data):
    """
    Generate a QR code for the given data.
    """
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)

    return qr.make_image()