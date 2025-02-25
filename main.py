import subprocess
import os
import sys
import argparse
from pathlib import Path
from datetime import datetime

# Create directories
data_dir = Path("data")
data_dir.mkdir(parents=True, exist_ok=True)


def check_dependencies():
    """Check if required dependencies are installed"""
    dependencies = {"yt-dlp": False, "ffmpeg": False}

    # Check for yt-dlp
    try:
        import yt_dlp

        dependencies["yt-dlp"] = True
    except ImportError:
        print("yt-dlp is not installed. Installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp"])
            import yt_dlp

            dependencies["yt-dlp"] = True
            print("yt-dlp installed successfully")
        except Exception as e:
            print(f"Failed to install yt-dlp: {e}")

    # Check for ffmpeg
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        if result.returncode == 0:
            dependencies["ffmpeg"] = True
        else:
            print("ffmpeg is installed but returned an error.")
    except FileNotFoundError:
        print("ffmpeg is not installed or not in PATH")

    return all(dependencies.values()), dependencies


def download_video(url, output_path, filename):
    """
    Download video with the highest quality using yt-dlp.

    Args:
        url: YouTube URL
        output_path: Path to save the video
        filename: Name of the output file

    Returns:
        Path to the downloaded video
    """
    try:
        import yt_dlp
    except ImportError:
        print("Error: yt-dlp is required but not installed.")
        return None

    full_output_path = output_path / filename

    # Options for yt-dlp
    ydl_opts = {
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",  # More flexible format selection
        "outtmpl": str(full_output_path),
        "quiet": False,
        "no_warnings": False,
        "ignoreerrors": True,
        "verbose": True,  # Add verbose output for debugging
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Attempting to download from {url}...")
            info = ydl.extract_info(url, download=False)
            print(f"Found video: {info.get('title', 'Unknown title')}")
            print(
                f"Available formats: {[f['format'] for f in info.get('formats', [])][:3]}..."
            )
            ydl.download([url])

        if os.path.exists(full_output_path):
            file_size = os.path.getsize(full_output_path)
            print(
                f"Successfully downloaded video to {full_output_path} (Size: {file_size/1024/1024:.2f} MB)"
            )
            return full_output_path
        else:
            print(f"Error: File was not created at {full_output_path}")
            return None
    except Exception as e:
        print(f"Error downloading video: {str(e)}")
        return None


def cut_video(input_file, output_file, start_time, end_time):
    """
    Extracts a portion of a video using FFmpeg.

    Args:
        input_file: Path to the input video file
        output_file: Path to the output video file
        start_time: Start time of the cut in `HH:MM:SS` format
        end_time: End time of the cut in `HH:MM:SS` format
    """

    def time_to_seconds(time_str):
        t = datetime.strptime(time_str, "%H:%M:%S")
        return t.hour * 3600 + t.minute * 60 + t.second

    start_sec = time_to_seconds(start_time)
    end_sec = time_to_seconds(end_time)
    duration = end_sec - start_sec

    # More compatible FFmpeg command with fallback options
    commands = [
        # First attempt: High quality with specified codecs
        [
            "ffmpeg",
            "-y",
            "-ss",
            str(start_sec),
            "-i",
            str(input_file),
            "-t",
            str(duration),
            "-c:v",
            "libx264",
            "-crf",
            "23",
            "-preset",
            "medium",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            str(output_file),
        ],
        # Second attempt: Copy codec (faster but may have accuracy issues at cut points)
        [
            "ffmpeg",
            "-y",
            "-ss",
            str(start_sec),
            "-i",
            str(input_file),
            "-t",
            str(duration),
            "-c",
            "copy",
            str(output_file),
        ],
        # Last resort: Basic settings
        [
            "ffmpeg",
            "-y",
            "-ss",
            str(start_sec),
            "-i",
            str(input_file),
            "-t",
            str(duration),
            str(output_file),
        ],
    ]

    success = False
    for i, command in enumerate(commands):
        try:
            print(f"Attempt {i+1}: Running FFmpeg...")
            print(" ".join(command))
            result = subprocess.run(
                command, check=True, stderr=subprocess.PIPE, text=True
            )
            success = True
            print(f"Successfully cut video to {output_file}")
            break
        except subprocess.CalledProcessError as e:
            print(f"Attempt {i+1} failed: {e}")
            print(f"FFmpeg error output: {e.stderr}")
            if i == len(commands) - 1:
                print("All cutting attempts failed")

    return success


def validate_time_format(time_str):
    """Validate if the time string is in HH:MM:SS format"""
    try:
        datetime.strptime(time_str, "%H:%M:%S")
        return True
    except ValueError:
        return False


def get_user_input():
    """Get user input for video parameters"""
    parser = argparse.ArgumentParser(description="Download and cut a YouTube video")

    # Add command-line arguments
    parser.add_argument("--url", type=str, help="YouTube video URL")
    parser.add_argument("--name", type=str, help="Output video filename")
    parser.add_argument("--start", type=str, help="Start time (HH:MM:SS)")
    parser.add_argument("--end", type=str, help="End time (HH:MM:SS)")
    parser.add_argument(
        "--skip-download",
        action="store_true",
        help="Skip download and use existing file",
    )
    parser.add_argument(
        "--skip-cut", action="store_true", help="Skip cutting, download only"
    )

    args = parser.parse_args()

    # If arguments weren't provided via command line, prompt the user
    video_url = args.url
    if not video_url and not args.skip_download:
        video_url = input("Enter YouTube video URL: ")

    video_name = args.name
    if not video_name:
        video_name = input("Enter output video filename (e.g., video.mp4): ")
        if not video_name.endswith(".mp4"):
            video_name += ".mp4"

    start_time = args.start
    if not args.skip_cut:
        while not start_time or not validate_time_format(start_time):
            start_time = input("Enter start time (HH:MM:SS format): ")
            if not validate_time_format(start_time):
                print("Invalid time format. Please use HH:MM:SS")

    end_time = args.end
    if not args.skip_cut:
        while not end_time or not validate_time_format(end_time):
            end_time = input("Enter end time (HH:MM:SS format): ")
            if not validate_time_format(end_time):
                print("Invalid time format. Please use HH:MM:SS")

    return (
        video_url,
        video_name,
        start_time,
        end_time,
        args.skip_download,
        args.skip_cut,
    )


if __name__ == "__main__":
    print("Video Downloader and Cutter Tool")
    print("================================")

    # Check dependencies
    all_deps_installed, deps_status = check_dependencies()
    if not all_deps_installed:
        print("\nWarning: Some dependencies are missing:")
        for dep, installed in deps_status.items():
            status = "✓ Installed" if installed else "✗ Not installed"
            print(f"  - {dep}: {status}")

        proceed = input("\nDo you want to proceed anyway? (y/n): ")
        if proceed.lower() != "y":
            print("Exiting...")
            sys.exit(1)

    # Get user input
    video_url, video_name, start_time, end_time, skip_download, skip_cut = (
        get_user_input()
    )

    input_video = None
    if skip_download:
        # Use existing file
        input_video = data_dir / video_name
        if not os.path.exists(input_video):
            print(
                f"Error: File {input_video} does not exist for --skip-download option."
            )
            sys.exit(1)
        print(f"Using existing video file: {input_video}")
    else:
        # Download video
        print(f"\nDownloading video from: {video_url}")
        input_video = download_video(video_url, data_dir, video_name)

    if input_video and os.path.exists(input_video):
        if skip_cut:
            print(f"Download complete. Skipping cutting as requested.")
            sys.exit(0)

        # Generate output filename
        output_video_name = f"cut_{video_name}"
        output_video = data_dir / output_video_name

        print(f"\nCutting video from {start_time} to {end_time}")
        success = cut_video(input_video, output_video, start_time, end_time)

        if success and os.path.exists(output_video):
            print(f"\nVideo cut successfully. Output saved to: {output_video}")
            print(f"File size: {os.path.getsize(output_video)/1024/1024:.2f} MB")
        else:
            print("\nFailed to create cut video")
    else:
        print("\nFailed to download or find video")
