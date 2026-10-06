import json
import os
import subprocess
import sys


def format_file_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} Bytes"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes / (1024 ** 2):.2f} MB"
    return f"{size_bytes / (1024 ** 3):.2f} GB"


def format_duration(seconds):
    try:
        seconds = float(seconds)
    except (TypeError, ValueError):
        return "Not Available"

    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:05.2f}"


def parse_frame_rate(value):
    if not value or value == "0/0":
        return "Not Available"

    try:
        numerator, denominator = value.split("/")
        denominator = float(denominator)
        if denominator == 0:
            return "Not Available"
        return f"{float(numerator) / denominator:.2f} FPS"
    except Exception:
        return str(value)


def run_ffprobe(file_path):
    command = [
        "ffprobe",
        "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        "-show_streams",
        file_path,
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)

    except FileNotFoundError:
        print("Error: FFmpeg/ffprobe is not installed or not added to PATH.")
        print("Install FFmpeg and try again.")
        return None

    except subprocess.CalledProcessError:
        print("Error: Could not read video metadata.")
        return None

    except json.JSONDecodeError:
        print("Error: Invalid metadata returned by ffprobe.")
        return None


def extract_video_metadata(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File '{file_path}' does not exist.")

    data = run_ffprobe(file_path)
    if data is None:
        return None

    format_info = data.get("format", {})
    streams = data.get("streams", [])

    video_stream = next(
        (stream for stream in streams if stream.get("codec_type") == "video"),
        {}
    )
    audio_stream = next(
        (stream for stream in streams if stream.get("codec_type") == "audio"),
        {}
    )

    width = video_stream.get("width")
    height = video_stream.get("height")

    if width and height:
        resolution = f"{width} x {height}"
    else:
        resolution = "Not Available"

    container = format_info.get("format_long_name") or format_info.get("format_name", "Not Available")

    metadata = {
        "file_name": os.path.basename(file_path),
        "file_size": format_file_size(os.path.getsize(file_path)),
        "container": container,
        "duration": format_duration(format_info.get("duration")),
        "video": {
            "resolution": resolution,
            "frame_rate": parse_frame_rate(
                video_stream.get("avg_frame_rate")
                or video_stream.get("r_frame_rate")
            ),
            "bit_rate": (
                f"{int(video_stream['bit_rate']) / 1000:.2f} kbps"
                if video_stream.get("bit_rate")
                else "Not Available"
            ),
            "codec": (
                video_stream.get("codec_long_name")
                or video_stream.get("codec_name")
                or "Not Available"
            ),
        },
        "audio": {
            "codec": (
                audio_stream.get("codec_long_name")
                or audio_stream.get("codec_name")
                or "Not Available"
            ),
            "channels": audio_stream.get("channels", "Not Available"),
            "sampling_rate": (
                f"{audio_stream.get('sample_rate')} Hz"
                if audio_stream.get("sample_rate")
                else "Not Available"
            ),
            "bit_rate": (
                f"{int(audio_stream['bit_rate']) / 1000:.2f} kbps"
                if audio_stream.get("bit_rate")
                else "Not Available"
            ),
        },
        "metadata": format_info.get("tags", {}) or {},
    }

    return metadata


def print_report(metadata):
    print("\n================================")
    print("VIDEO METADATA REPORT")
    print("================================\n")

    print(f"{'File Name':<16}: {metadata['file_name']}")
    print(f"{'File Size':<16}: {metadata['file_size']}")
    print(f"{'Container':<16}: {metadata['container']}")
    print(f"{'Duration':<16}: {metadata['duration']}")

    print("\nVIDEO")
    print("--------------------------------")
    print(f"{'Resolution':<16}: {metadata['video']['resolution']}")
    print(f"{'Frame Rate':<16}: {metadata['video']['frame_rate']}")
    print(f"{'Bit Rate':<16}: {metadata['video']['bit_rate']}")
    print(f"{'Codec':<16}: {metadata['video']['codec']}")

    print("\nAUDIO")
    print("--------------------------------")
    print(f"{'Codec':<16}: {metadata['audio']['codec']}")
    print(f"{'Channels':<16}: {metadata['audio']['channels']}")
    print(f"{'Sampling Rate':<16}: {metadata['audio']['sampling_rate']}")
    print(f"{'Bit Rate':<16}: {metadata['audio']['bit_rate']}")

    print("\nMETADATA")
    print("--------------------------------")

    if metadata["metadata"]:
        for key, value in metadata["metadata"].items():
            print(f"{str(key):<16}: {value}")
    else:
        print("No additional metadata found.")


def analyze_video(file_path):
    try:
        metadata = extract_video_metadata(file_path)
        if metadata:
            print_report(metadata)
        return metadata
    except FileNotFoundError as error:
        print(f"Error: {error}")
        return None
    except Exception as error:
        print(f"Error while analyzing video: {error}")
        return None


def main():
    if len(sys.argv) >= 2:
        file_path = " ".join(sys.argv[1:])
    else:
        file_path = input("Enter video path: ").strip()

    file_path = file_path.strip('"').strip("'")
    analyze_video(file_path)


if __name__ == "__main__":
    main()
