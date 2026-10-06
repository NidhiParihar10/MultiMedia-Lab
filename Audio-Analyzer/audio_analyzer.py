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

    minutes = int(seconds // 60)
    secs = seconds % 60
    return f"{minutes:02d}:{secs:05.2f}"


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
        print("Error: Could not read audio metadata.")
        return None

    except json.JSONDecodeError:
        print("Error: Invalid metadata returned by ffprobe.")
        return None


def extract_audio_metadata(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File '{file_path}' does not exist.")

    if not os.path.isfile(file_path):
        raise ValueError("Provided path is not a file.")

    data = run_ffprobe(file_path)
    if data is None:
        return None

    format_info = data.get("format", {})
    streams = data.get("streams", [])

    audio_stream = next(
        (stream for stream in streams if stream.get("codec_type") == "audio"),
        {}
    )

    container = (
        format_info.get("format_long_name")
        or format_info.get("format_name")
        or "Not Available"
    )

    codec = (
        audio_stream.get("codec_long_name")
        or audio_stream.get("codec_name")
        or "Not Available"
    )

    channels = audio_stream.get("channels", "Not Available")

    channel_layout = audio_stream.get("channel_layout", "Not Available")

    sample_rate = audio_stream.get("sample_rate")
    sampling_rate = (
        f"{sample_rate} Hz"
        if sample_rate
        else "Not Available"
    )

    bit_rate_value = (
        audio_stream.get("bit_rate")
        or format_info.get("bit_rate")
    )

    if bit_rate_value:
        try:
            bit_rate = f"{int(bit_rate_value) / 1000:.2f} kbps"
        except (TypeError, ValueError):
            bit_rate = str(bit_rate_value)
    else:
        bit_rate = "Not Available"

    metadata = {
        "file_name": os.path.basename(file_path),
        "file_size": format_file_size(os.path.getsize(file_path)),
        "container": container,
        "duration": format_duration(format_info.get("duration")),
        "codec": codec,
        "channels": channels,
        "channel_layout": channel_layout,
        "sampling_rate": sampling_rate,
        "bit_rate": bit_rate,
        "metadata": format_info.get("tags", {}) or {},
    }

    return metadata


def print_report(metadata):
    print("\n================================")
    print("AUDIO METADATA REPORT")
    print("================================\n")

    print(f"{'File Name':<16}: {metadata['file_name']}")
    print(f"{'File Size':<16}: {metadata['file_size']}")
    print(f"{'Container':<16}: {metadata['container']}")
    print(f"{'Duration':<16}: {metadata['duration']}")

    print("\nAUDIO")
    print("--------------------------------")
    print(f"{'Codec':<16}: {metadata['codec']}")
    print(f"{'Channels':<16}: {metadata['channels']}")
    print(f"{'Channel Layout':<16}: {metadata['channel_layout']}")
    print(f"{'Sampling Rate':<16}: {metadata['sampling_rate']}")
    print(f"{'Bit Rate':<16}: {metadata['bit_rate']}")

    print("\nMETADATA")
    print("--------------------------------")

    if metadata["metadata"]:
        for key, value in metadata["metadata"].items():
            print(f"{str(key):<16}: {value}")
    else:
        print("No additional metadata found.")


def analyze_audio(file_path):
    try:
        metadata = extract_audio_metadata(file_path)

        if metadata:
            print_report(metadata)

        return metadata

    except FileNotFoundError as error:
        print(f"Error: {error}")
        return None

    except ValueError as error:
        print(f"Error: {error}")
        return None

    except Exception as error:
        print(f"Error while analyzing audio: {error}")
        return None


def main():
    if len(sys.argv) >= 2:
        file_path = " ".join(sys.argv[1:])
    else:
        file_path = input("Enter audio path: ").strip()

    file_path = file_path.strip('"').strip("'")

    analyze_audio(file_path)


if __name__ == "__main__":
    main()
