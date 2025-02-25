# YouTube Video Downloader & Editor

This project automates the process of downloading YouTube videos and cutting specific portions based on timestamp values using `yt-dlp` and `ffmpeg`.

## **Setup Instructions**

### **1. Set Up Project Repository**
1. Create a new repository on GitHub.
2. Clone the repository locally:
   ```bash
   git clone <your-repo-url>
   cd <repo-name>
   code .  # Opens VS Code
   ```

### **2. Install UV Package Manager**
UV is a fast, modern Python package manager.

#### **Option 1 (Recommended)**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
To update UV later:
```bash
uv self update
```

#### **Option 2**
```bash
pip install uv
```

### **3. Initialize Python Environment**
```bash
uv init --python 3.10.11
```

### **4. Install Required Packages**
```bash
uv add datetime ffmpeg ipykernel ipython pathlib yt-dlp
```

## **Installing FFmpeg on Windows**
FFmpeg is required for processing video files.

### **Download from Official Site**
1. Visit [Gyan.dev FFmpeg Builds](https://www.gyan.dev/ffmpeg/builds/).
2. Download the latest **FFmpeg Release Build** (`.zip` file).
3. Extract the ZIP file to a folder (e.g., `C:\ffmpeg`).
4. Add FFmpeg to the system **Path**:
   - Press `Win + R`, type `sysdm.cpl`, and hit **Enter**.
   - Go to **Advanced** → **Environment Variables**.
   - Under **System Variables**, find `Path` and click **Edit**.
   - Click **New** and add:
     ```
     C:\ffmpeg\bin
     ```
   - Click **OK** → **Apply** → **OK**.
5. Verify the installation:
   ```cmd
   ffmpeg -version
   ```

## **Usage Instructions**
The script expects the user to input:
- A **YouTube video URL**
- A **video name** (for saving the downloaded file)
- **Start time** and **end time** for the portion of the video to be cut

Example test URL:
```
https://youtu.be/ad-skW0SWeE?list=TLPQMjUwMjIwMjVBkI3Yxog-4w
```

Your system is now set up to run the YouTube video downloader and editor script!

