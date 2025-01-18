from pathlib import Path

import yt_dlp
from loguru import logger

DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)


def get_yt_info(url: str) -> dict:
    """Get video info from YouTube URL."""
    ydl_opts = {"quiet": True, "no_warnings": True, "extract_flat": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            return {
                "title": info.get("title"),
                "thumbnail": info.get("thumbnail"),
                "duration": info.get("duration"),
                "channel": info.get("uploader"),
                "views": info.get("view_count"),
            }
        except Exception as e:
            logger.error(f"Error getting video info: {e}")
            return None


def download_video(url: str, quality="best") -> str:
    """Download video at specified quality."""
    ydl_opts = {
        "format": quality,
        "outtmpl": str(DOWNLOAD_DIR / "%(title)s.%(ext)s"),
        "progress_hooks": [_progress_hook],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=True)
            return str(DOWNLOAD_DIR / f"{info['title']}.{info['ext']}")
        except Exception as e:
            logger.error(f"Error downloading video: {e}")
            return None


def _progress_hook(d):
    """Progress hook for download status."""
    if d["status"] == "downloading":
        progress = (
            float(d.get("downloaded_bytes", 0)) / float(d.get("total_bytes", 1)) * 100
        )
        logger.info(f"Download progress: {progress:.1f}%")
    elif d["status"] == "finished":
        logger.info("Download completed successfully")
