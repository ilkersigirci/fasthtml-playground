import json

from fasthtml.common import *
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

app, rt = fast_app()


@rt("/")
def get():
    search_form = Form(
        Input(id="search", name="search", placeholder="Search YouTube videos..."),
        Button("Search", type="submit"),
        hx_post="/search",
        hx_target="#results",
        hx_indicator=".htmx-indicator",
    )

    return Titled(
        "YouTube Downloader",
        Container(
            search_form,
            Div(cls="htmx-indicator", style="display:none")("Searching..."),
            Div(id="results"),
        ),
    )


@rt("/search")
def post(search: str):
    if not search:
        return "Please enter a search term"

    ydl_opts = {"quiet": True, "extract_flat": True, "no_warnings": True}

    try:
        with YoutubeDL(ydl_opts) as ydl:
            results = ydl.extract_info(f"ytsearch5:{search}", download=False)

        if not results.get("entries"):
            return "No results found"

        grid = Grid()
        for video in results["entries"]:
            card = Card(
                H3(video["title"]),
                Img(src=video.get("thumbnail", ""), alt=video["title"]),
                footer=Button(
                    "Download",
                    hx_post=f"/download/{video['id']}",
                    hx_target="#progress",
                    cls="download-btn",
                ),
            )
            grid.append(card)

        return Div(grid, Div(id="progress"))
    except Exception as e:
        return f"Error searching: {str(e)}"


@rt("/download/{video_id}")
async def post(video_id: str):  # Remove send parameter
    progress_id = f"progress-{video_id}"

    def progress_hook(d):
        if d["status"] == "downloading":
            progress = d.get("_percent_str", "0%").strip()
            # Create a progress div
            return Div(f"Downloading: {progress}", id=progress_id, hx_swap_oob="true")

    ydl_opts = {
        "progress_hooks": [progress_hook],
        "quiet": True,
        "no_warnings": True,
        "format": "best",
        "outtmpl": "downloads/%(title)s.%(ext)s",
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            await ydl.download([f"https://www.youtube.com/watch?v={video_id}"])
            return Div("Download complete!", id=progress_id, hx_swap_oob="true")
    except Exception as e:
        return Div(f"Error downloading: {str(e)}", id=progress_id, hx_swap_oob="true")
