import pytest
from bs4 import BeautifulSoup
from postprocess import video_mime_types, fix_image_video_tags

def test_fix_image_video_tags_video_conversion():
    html_input = '''
    <img alt="" src="screen-20241026-203745_1.mp4">
    <img alt="" src="/m/PXL_20241026_233647996.jpg">
    '''
    expected_output = '''
    <video controls="True" width="300"><source src="screen-20241026-203745_1.mp4" type="video/mp4"/>This text is displayed if your browser does not support the video tag.</video>
    <img alt="" src="/m/PXL_20241026_233647996.jpg"/>
    '''


    converted_html = fix_image_video_tags(html_input)

    # Normalize whitespace to ensure matching is only content-based
    assert BeautifulSoup(converted_html, "html.parser").prettify() == BeautifulSoup(expected_output, "html.parser").prettify()

def test_fix_image_video_tags_no_conversion_needed():
    html_input = '''
    <img alt="" src="/m/PXL_20241026_233647996.jpg">
    <img alt="" src="/m/image.png">
    '''

    expected_output = html_input  # No conversion should occur

    converted_html = fix_image_video_tags(html_input)

    assert BeautifulSoup(converted_html, "html.parser").prettify() == BeautifulSoup(expected_output, "html.parser").prettify()

def test_fix_image_video_tags_mixed_media():
    html_input = '''
    <img alt="" src="video.webm">
    <img alt="" src="music.mp3">
    <img alt="" src="photo.png">
    <img alt="" src="clip.avi">
    '''

    expected_output = '''
    <video controls="True" width="300"><source src="video.webm" type="video/webm"/>This text is displayed if your browser does not support the video tag.</video>
    <img alt="" src="music.mp3"/>
    <img alt="" src="photo.png"/>
    <video controls="True" width="300"><source src="clip.avi" type="video/x-msvideo"/>This text is displayed if your browser does not support the video tag.</video>
    '''

    converted_html = fix_image_video_tags(html_input)

    assert BeautifulSoup(converted_html, "html.parser").prettify() == BeautifulSoup(expected_output, "html.parser").prettify()

if __name__ == "__main__":
    # test_fix_image_video_tags_mixed_media()
    pytest.main()
