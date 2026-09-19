import os
from PIL import Image, ImageDraw, ImageFont

def generate_sample_passport(filename, is_tampered=False):
    """
    Generates synthetic sample passport images with embedded MRZ text.
    
    For tampered samples: the MRZ line2 ends with a deliberately wrong composite 
    check digit, and the photo region uses a visually distinct red fill.
    This produces genuinely different ELA signatures and checksum failures
    when processed through the real pipeline — no hardcoded score overrides needed.
    """
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

    if is_tampered and "mismatch" in filename.lower():
        # MISMATCH VARIANT: Visual text shows DIFFERENT values than MRZ
        # Photo Box (Left) — normal color but different person name
        photo_box = [(40, 110), (240, 370)]
        draw.rectangle(photo_box, fill=(51, 65, 85), outline=(30, 41, 59), width=3)
        draw.text((75, 230), "[ PHOTO ROI ]", fill=(255, 255, 255))

        # Visual text fields show DIFFERENT data than what's in MRZ
        draw.text((280, 110), "Surname / Nom:", fill=(100, 116, 139))
        draw.text((280, 130), "VERMA", fill=(15, 23, 42))

        draw.text((280, 160), "Given Names / Prénom:", fill=(100, 116, 139))
        draw.text((280, 180), "PRIYA DEVI", fill=(15, 23, 42))

        draw.text((280, 210), "Nationality / Nationalité:", fill=(100, 116, 139))
        draw.text((280, 230), "INDIAN", fill=(15, 23, 42))

        draw.text((280, 260), "Date of Birth / Date de naissance:", fill=(100, 116, 139))
        draw.text((280, 280), "1995-11-22", fill=(15, 23, 42))

        draw.text((280, 310), "Sex / Sexe:", fill=(100, 116, 139))
        draw.text((280, 330), "F", fill=(15, 23, 42))

        draw.text((500, 260), "Date of Expiry / Date d'expiration:", fill=(100, 116, 139))
        draw.text((500, 280), "2031-06-15", fill=(15, 23, 42))

        draw.text((500, 110), "Passport No / N° de passeport:", fill=(100, 116, 139))
        draw.text((500, 130), "K5614782", fill=(15, 23, 42))

        # MRZ Zone — uses DIFFERENT name/number than visual text above
        # This creates a real mismatch detectable by the pipeline
        draw.rectangle([(0, 420), (width, height)], fill=(15, 23, 42))
        line1 = "P<INDGUPTA<<ANITA<RANI<<<<<<<<<<<<<<<<<<<<"
        line2 = "K5614789<3IND9511221F3106152<<<<<<<<<<<<<<0"
        draw.text((40, 445), line1, fill=(56, 189, 248))
        draw.text((40, 490), line2, fill=(56, 189, 248))

    elif is_tampered:
        # TAMPERED VARIANT: Deliberately altered photo region (red overlay) + invalid checksum
        photo_box = [(40, 110), (240, 370)]
        photo_fill = (185, 28, 28)  # Red tint — tampered photo
        draw.rectangle(photo_box, fill=photo_fill, outline=(30, 41, 59), width=3)
        # Draw fake patch overlay in photo box — creates different ELA signature
        draw.rectangle([(50, 120), (230, 260)], fill=(225, 29, 72), outline=(255, 255, 255), width=2)
        draw.text((65, 180), "TAMPERED PHOTO", fill=(255, 255, 255))
        # Additional digital noise overlay to amplify ELA difference
        import random
        random.seed(42)  # Reproducible noise
        for _ in range(500):
            rx = random.randint(50, 230)
            ry = random.randint(120, 360)
            rc = (random.randint(150, 255), random.randint(0, 80), random.randint(0, 80))
            draw.point((rx, ry), fill=rc)

        # Text Fields
        draw.text((280, 110), "Surname / Nom:", fill=(100, 116, 139))
        draw.text((280, 130), "SHARMA", fill=(15, 23, 42))

        draw.text((280, 160), "Given Names / Prénom:", fill=(100, 116, 139))
        draw.text((280, 180), "RAHUL KUMAR", fill=(15, 23, 42))

        draw.text((280, 210), "Nationality / Nationalité:", fill=(100, 116, 139))
        draw.text((280, 230), "INDIAN", fill=(15, 23, 42))

        draw.text((280, 260), "Date of Birth / Date de naissance:", fill=(100, 116, 139))
        draw.text((280, 280), "1988-03-12 (ALTERED)", fill=(225, 29, 72))

        draw.text((280, 310), "Sex / Sexe:", fill=(100, 116, 139))
        draw.text((280, 330), "M", fill=(15, 23, 42))

        draw.text((500, 260), "Date of Expiry / Date d'expiration:", fill=(100, 116, 139))
        draw.text((500, 280), "2029-10-24", fill=(15, 23, 42))

        draw.text((500, 110), "Passport No / N° de passeport:", fill=(100, 116, 139))
        draw.text((500, 130), "J8293041", fill=(15, 23, 42))

        # MRZ Zone — invalid composite check digit (9 instead of correct)
        draw.rectangle([(0, 420), (width, height)], fill=(15, 23, 42))
        line1 = "P<INDSHARMA<<RAHUL<KUMAR<<<<<<<<<<<<<<<<<<<<"
        line2 = "J8293041<4IND9205141M2910248<<<<<<<<<<<<<<<9"  # Wrong composite digit
        draw.text((40, 445), line1, fill=(56, 189, 248))
        draw.text((40, 490), line2, fill=(56, 189, 248))

    else:
        # AUTHENTIC VARIANT: Clean scan, valid checksums
        photo_box = [(40, 110), (240, 370)]
        draw.rectangle(photo_box, fill=(51, 65, 85), outline=(30, 41, 59), width=3)
        draw.text((75, 230), "[ PHOTO ROI ]", fill=(255, 255, 255))

        # Text Fields
        draw.text((280, 110), "Surname / Nom:", fill=(100, 116, 139))
        draw.text((280, 130), "SHARMA", fill=(15, 23, 42))

        draw.text((280, 160), "Given Names / Prénom:", fill=(100, 116, 139))
        draw.text((280, 180), "RAHUL KUMAR", fill=(15, 23, 42))

        draw.text((280, 210), "Nationality / Nationalité:", fill=(100, 116, 139))
        draw.text((280, 230), "INDIAN", fill=(15, 23, 42))

        draw.text((280, 260), "Date of Birth / Date de naissance:", fill=(100, 116, 139))
        draw.text((280, 280), "1992-05-14", fill=(15, 23, 42))

        draw.text((280, 310), "Sex / Sexe:", fill=(100, 116, 139))
        draw.text((280, 330), "M", fill=(15, 23, 42))

        draw.text((500, 260), "Date of Expiry / Date d'expiration:", fill=(100, 116, 139))
        draw.text((500, 280), "2029-10-24", fill=(15, 23, 42))

        draw.text((500, 110), "Passport No / N° de passeport:", fill=(100, 116, 139))
        draw.text((500, 130), "J8293041", fill=(15, 23, 42))

        # MRZ Zone — valid checksums
        draw.rectangle([(0, 420), (width, height)], fill=(15, 23, 42))
        line1 = "P<INDSHARMA<<RAHUL<KUMAR<<<<<<<<<<<<<<<<<<<<"
        line2 = "J8293041<2IND9205141M2910242<<<<<<<<<<<<<<<0"
        draw.text((40, 445), line1, fill=(56, 189, 248))
        draw.text((40, 490), line2, fill=(56, 189, 248))

    img.save(file_path, "JPEG", quality=95)
    print(f"Generated sample: {file_path}")


if __name__ == "__main__":
    generate_sample_passport("sample_authentic_passport.jpg", is_tampered=False)
    generate_sample_passport("sample_tampered_passport.jpg", is_tampered=True)
    generate_sample_passport("sample_mismatch_visa.jpg", is_tampered=True)
