import pytesseract

def perform_ocr_on_image(image):
    return pytesseract.image_to_string(image)
