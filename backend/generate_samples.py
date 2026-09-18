import os
from PIL import Image, ImageDraw, ImageFont

def generate_sample_passport(filename, is_tampered=False):
    samples_dir = os.path.join(os.path.dirname(__file__), "static", "samples")
    os.makedirs(samples_dir, exist_ok=True)
    file_path = os.path.join(samples_dir, filename)

    # Create document canvas
    width, height = 850, 560
    bg_color = (248, 250, 252) if not is_tampered else (241, 245, 249)
    img = Image.new("RGB", (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)

    # Header Bar
    draw.rectangle([(0, 0), (width, 80)], fill=(15, 23, 42))
    draw.text((30, 25), "REPUBLIC OF INDIA  /  PASSPORT", fill=(255, 255, 255))
    draw.text((700, 25), "TYPE: P", fill=(203, 213, 225))

    # Photo Box (Left)
    photo_box = [(40, 110), (240, 370)]
    photo_fill = (51, 65, 85) if not is_tampered else (185, 28, 28) # Red tint if tampered
    draw.rectangle(photo_box, fill=photo_fill, outline=(30, 41, 59), width=3)
    draw.text((75, 230), "[ PHOTO ROI ]", fill=(255, 255, 255))

    if is_tampered:
        # Draw fake patch overlay in photo box
        draw.rectangle([(50, 120), (230, 260)], fill=(225, 29, 72), outline=(255, 255, 255), width=2)
        draw.text((65, 180), "TAMPERED PHOTO", fill=(255, 255, 255))

    # Text Fields (Right)
    draw.text((280, 110), "Surname / Nom:", fill=(100, 116, 139))
    draw.text((280, 130), "SHARMA", fill=(15, 23, 42))

    draw.text((280, 160), "Given Names / Prénom:", fill=(100, 116, 139))
    draw.text((280, 180), "RAHUL KUMAR", fill=(15, 23, 42))

    draw.text((280, 210), "Nationality / Nationalité:", fill=(100, 116, 139))
    draw.text((280, 230), "INDIAN", fill=(15, 23, 42))

    draw.text((280, 260), "Date of Birth / Date de naissance:", fill=(100, 116, 139))
    dob_text = "1992-05-14" if not is_tampered else "1988-03-12 (ALTERED)"
    dob_color = (15, 23, 42) if not is_tampered else (225, 29, 72)
    draw.text((280, 280), dob_text, fill=dob_color)

    draw.text((280, 310), "Sex / Sexe:", fill=(100, 116, 139))
    draw.text((280, 330), "M", fill=(15, 23, 42))

    draw.text((500, 260), "Date of Expiry / Date d'expiration:", fill=(100, 116, 139))
    draw.text((500, 280), "2029-10-24", fill=(15, 23, 42))

    draw.text((500, 110), "Passport No / N° de passeport:", fill=(100, 116, 139))
    draw.text((500, 130), "J8293041", fill=(15, 23, 42))

    # MRZ Zone (Bottom)
    draw.rectangle([(0, 420), (width, height)], fill=(15, 23, 42))
    
    line1 = "P<INDSHARMA<<RAHUL<KUMAR<<<<<<<<<<<<<<<<<<<"
    line2 = "J8293041<4IND9205141M2910248<<<<<<<<<<<<<<<0"
    if is_tampered:
        line2 = "J8293041<4IND9205141M2910248<<<<<<<<<<<<<<<9" # Invalid checksum digit 9

    draw.text((40, 445), line1, fill=(56, 189, 248))
    draw.text((40, 490), line2, fill=(56, 189, 248))

    img.save(file_path, "JPEG", quality=95)
    print(f"Generated sample: {file_path}")

if __name__ == "__main__":
    generate_sample_passport("sample_authentic_passport.jpg", is_tampered=False)
    generate_sample_passport("sample_tampered_passport.jpg", is_tampered=True)
    generate_sample_passport("sample_mismatch_visa.jpg", is_tampered=True)
