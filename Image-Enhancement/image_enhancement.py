import cv2
import os
import numpy as np


def enhance_image(image_path):

    if not os.path.exists(image_path):
        print("Error: Image file does not exist.")
        return

    image = cv2.imread(image_path)

    if image is None:
        print("Error: Unable to read image.")
        return

    print("\n================================")
    print("IMAGE ENHANCEMENT")
    print("================================")

    print("Input Image :", os.path.basename(image_path))
    print("Original Size:", image.shape[1], "x", image.shape[0])

    # Noise Reduction
    denoised = cv2.fastNlMeansDenoisingColored(
        image, None, 5, 5, 7, 21
    )

    # Contrast Enhancement
    lab = cv2.cvtColor(denoised, cv2.COLOR_BGR2LAB)

    l, a, b = cv2.split(lab)

    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    enhanced_l = clahe.apply(l)

    enhanced_lab = cv2.merge(
        (enhanced_l, a, b)
    )

    enhanced = cv2.cvtColor(
        enhanced_lab,
        cv2.COLOR_LAB2BGR
    )

    # Sharpening
    kernel = np.array([
        [0, -1, 0],
        [-1, 5, -1],
        [0, -1, 0]
    ])

    sharpened = cv2.filter2D(
        enhanced,
        -1,
        kernel
    )

    os.makedirs("output", exist_ok=True)

    output_path = "output/enhanced_image.jpg"

    cv2.imwrite(output_path, sharpened)

    print("\nEnhancement Applied:")
    print("- Noise Reduction")
    print("- Contrast Enhancement")
    print("- Sharpening")

    print("\nIMAGE ENHANCEMENT COMPLETE")
    print("Output File:", output_path)


def main():

    image_path = input(
        "Enter image path: "
    ).strip().strip('"')

    enhance_image(image_path)


if __name__ == "__main__":
    main()