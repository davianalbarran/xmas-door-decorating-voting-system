# QR Code Imports
import qrcode
import qrcode.constants
import os
import argparse
from typing import List

class DoorQrGenerator():
    qr = qrcode.QRCode(
        version=1, 
        error_correction=qrcode.constants.ERROR_CORRECT_L, 
        box_size=10, 
        border=4
    )

    def generate_qr(self, door_id: int, hostname: str):
        self.qr.add_data(f"{hostname}/vote/{door_id}")
        
        self.qr.make(fit=True)

        doors_path = 'doors'

        os.makedirs(doors_path, exist_ok=True)

        img = self.qr.make_image(fill_color="black", back_color="white")

        img.save(os.path.join(doors_path, f"{door_id}.png"))

        self.qr.clear()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("--host", type=str, default="localhost:8000", help="The hostname of the server hosting the voting system")
    parser.add_argument("--id", type=int, help="The door number you want to generate the QR code for")
    parser.add_argument("--ids", type=int, nargs='+', help="The door numbers you want to generate QR codes for")

    args = parser.parse_args()

    host = args.host
    id = args.id
    ids = args.ids

    if not (id is not None or ids is not None):
        print("You must supply either an id or a list of ids separated by spaces")
        exit(-1)
    
    generator = DoorQrGenerator()

    if id is not None:
        generator.generate_qr(int(id), host)
    
    if ids is not None:
        for id in ids:
            generator.generate_qr(int(id), host)
