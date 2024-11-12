from bs4 import BeautifulSoup


video_mime_types = {
    "mp4": "video/mp4",
    "webm": "video/webm",
    "ogg": "video/ogg",
    "ogv": "video/ogg",
    "avi": "video/x-msvideo",
    "mov": "video/quicktime",
    "wmv": "video/x-ms-wmv",
    "flv": "video/x-flv",
    "mkv": "video/x-matroska",
}


def fix_image_video_tags(html) -> str:
    soup = BeautifulSoup(html, "html.parser")

    images = soup.find_all("img")
    for img in images:
        src = img.get("src", "")
        # Extract file extension
        src_copy = src
        file_extension = src_copy.split(".")[-1].lower()

        # Check if the extension is in the video_mime_types
        if file_extension in video_mime_types:
            # Create a new video element
            video_tag = soup.new_tag("video", controls=True, width="300")
            source_tag = soup.new_tag(
                "source", src=src, type=video_mime_types[file_extension]
            )

            # Append source to video tag
            video_tag.append(source_tag)

            # Add fallback text
            video_tag.append(
                "This text is displayed if your browser does not support the video tag."
            )

            # Insert the new video tag in place of the existing img tag
            img.insert_before(video_tag)

            # Remove img tag after the video tag is inserted
            img.decompose()

    return str(soup)
