import os
import sys
from PIL import Image, ExifTags

SUPPORTED_FORMATS = {"JPEG", "PNG", "TIFF", "WEBP", "BMP"}

def format_file_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} Bytes"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.2f} KB"
    else:
        return f"{size_bytes / (1024 ** 2):.2f} MB"

def get_exif_metadata(image):
    metadata = {}
    try:
        exif_data = image.getexif()
        if not exif_data:
            return metadata

        for tag_id, value in exif_data.items():
            tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
            if isinstance(value, bytes):
                try:
                    value = value.decode(errors="ignore")
                except Exception:
                    value = str(value)
            metadata[tag_name] = value
    except Exception:
        pass
    return metadata

def print_value(label, value):
    print(f"{label:<16}: {value}")

def analyze_image(image_path):
    if not os.path.exists(image_path):
        print(f"Error: File '{image_path}' does not exist.")
        return

    if not os.path.isfile(image_path):
        print("Error: Provided path is not a file.")
        return

    try:
        with Image.open(image_path) as image:
            image_format = image.format

            if image_format not in SUPPORTED_FORMATS:
                print(f"Warning: {image_format} is not officially supported.")

            file_name = os.path.basename(image_path)
            file_size = os.path.getsize(image_path)
            width, height = image.size
            color_mode = image.mode

            dpi = image.info.get("dpi")
            if dpi:
                try:
                    resolution = f"{dpi[0]:.0f} x {dpi[1]:.0f} DPI"
                except (TypeError, IndexError):
                    resolution = str(dpi)
            else:
                resolution = "Not Available"

            print("\n================================")
            print("IMAGE METADATA REPORT")
            print("================================\n")

            print_value("File Name", file_name)
            print_value("File Size", format_file_size(file_size))
            print_value("File Format", image_format)
            print_value("Width", f"{width} pixels")
            print_value("Height", f"{height} pixels")
            print_value("Resolution", resolution)
            print_value("Color Mode", color_mode)

            print("\nEXIF Metadata")
            print("-------------------------------")

            exif = get_exif_metadata(image)
            if not exif:
                print("No EXIF metadata found.")
                return

            important_fields = {
                "Make": "Camera Make",
                "Model": "Camera",
                "DateTime": "Date Modified",
                "DateTimeOriginal": "Date Taken",
                "Orientation": "Orientation",
                "Software": "Software",
                "Artist": "Artist",
                "Copyright": "Copyright",
                "ExposureTime": "Exposure Time",
                "FNumber": "F Number",
                "ISOSpeedRatings": "ISO",
                "PhotographicSensitivity": "ISO",
                "FocalLength": "Focal Length",
                "Flash": "Flash",
                "LensModel": "Lens",
                "GPSInfo": "GPS Info"
            }

            displayed_tags = set()

            for exif_tag, display_name in important_fields.items():
                if exif_tag in exif:
                    print_value(display_name, exif[exif_tag])
                    displayed_tags.add(exif_tag)

            remaining = {
                key: value
                for key, value in exif.items()
                if key not in displayed_tags
            }

            if remaining:
                print("\nAdditional EXIF Metadata")
                print("-------------------------------")
                for key, value in remaining.items():
                    print_value(str(key), value)

    except Image.UnidentifiedImageError:
        print("Error: The file is not a valid or supported image.")
    except PermissionError:
        print("Error: Permission denied while accessing the image.")
    except Exception as error:
        print(f"Error while analyzing image: {error}")

def main():
    if len(sys.argv) >= 2:
        image_path = " ".join(sys.argv[1:])
    else:
        image_path = input("Enter image path: ").strip()

    image_path = image_path.strip('"').strip("'")
    analyze_image(image_path)

if __name__ == "__main__":
    main()
