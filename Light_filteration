import cv2
import numpy as np

def adjust_gamma(image, gamma=1.0):
    inv_gamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
    return cv2.LUT(image, table)

def remove_light_pollution(input_image_path, output_image_path):
    # Read the input image
    image = cv2.imread(input_image_path)
    
    # Apply gamma correction to improve overall brightness
    gamma_corrected = adjust_gamma(image, gamma=0.5)
    
    # Convert the image to the LAB color space
    lab = cv2.cvtColor(gamma_corrected, cv2.COLOR_BGR2LAB)
    
    # Split the LAB image into individual channels
    l, a, b = cv2.split(lab)
    
    # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization) to the L-channel
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    
    # Further adjust the A-channel to reduce yellow light pollution
    a = cv2.add(a, -15)
    
    # Merge the adjusted L and A channels with the original B channel
    lab = cv2.merge((l, a, b))
    
    # Convert the LAB image back to the BGR color space
    filtered_image = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    
    # Apply a bilateral filter to smooth the image while preserving edges
    filtered_image = cv2.bilateralFilter(filtered_image, d=9, sigmaColor=75, sigmaSpace=75)
    
    # Save the output image
    cv2.imwrite(output_image_path, filtered_image)

# Usage example
input_image_path = 'night_sky_with_light_pollution.jpg'
output_image_path = 'filtered_night_sky.jpg'
remove_light_pollution(input_image_path, output_image_path)
