from fasthtml.common import (
    H2,
    Button,
    Card,
    Div,
    Form,
    Img,
    Input,
    P,
    Style,
    Titled,
    fast_app,
)

from api.utils.youtube import download_video, get_yt_info

app, rt = fast_app()


@rt("/")
def get():
    search_form = Form(
        Input(type="text", id="url", name="url", placeholder="Enter YouTube URL"),
        Button("Search", hx_post="/search", hx_target="#results"),
        _cls="search-form",
    )

    return Titled(
        "YouTube Downloader",
        search_form,
        Div(id="results"),
        Div(id="download-progress"),
        Style("""
            .search-form { margin: 2em 0; }
            .video-card { border: 1px solid #ddd; padding: 1em; margin: 1em 0; }
            .video-info { margin: 1em 0; }
            .progress-bar { width: 100%; height: 20px; background: #eee; }
            .progress-bar-fill { height: 100%; width: 0%; background: #4CAF50; transition: width 0.3s; }
        """),
    )


@rt("/search")
def post(url: str):
    info = get_yt_info(url)
    if not info:
        return "Invalid URL or video not found"

    return Card(
        H2(info["title"]),
        Img(src=info["thumbnail"], width="320"),
        Div(
            P(f"Channel: {info['channel']}"),
            P(f"Views: {info['views']:,}"),
            P(f"Duration: {info['duration']} seconds"),
            _cls="video-info",
        ),
        Form(
            Button(
                "Download",
                hx_post=f"/download?url={url}",
                hx_target="#download-progress",
            ),
            _cls="download-form",
        ),
        _cls="video-card",
    )


@rt("/download")
def post(url: str):
    filepath = download_video(url)
    if filepath:
        return P(f"Download completed: {filepath}")
    return P("Download failed")
