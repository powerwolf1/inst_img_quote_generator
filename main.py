import textwrap
import requests
from PIL import Image, ImageDraw, ImageFont

from instagrapi import Client
from session import USERNAME, PASSWORD


SESSION_PATH = "session.json"


def get_quote():
    quote_details = {}

    if not quote_details:
        try:
            # first source:
            response = requests.get(
                "https://api.quotable.io/quotes/random",
                # available params: limit, maxLength, minLength, tags(tema), author
                params={"maxLength": "150", "tags": 'wisdom'},
                timeout=5,
                verify=False
            )
        except Exception as e:
            print(f"First source is out: {e}")
        else:
            if response.status_code == 200:
                content = response.json()[0].get('content')
                if content:
                    quote_details['quote'] = content
                    quote_details['author'] = response.json()[0].get('author')
                    quote_details['length'] = response.json()[0].get('length')
                    return quote_details

        # second source
        response = requests.post(
            "http://api.forismatic.com/api/1.0/",
            params={"method": "getQuote", "format": "json", "lang": "en"},
            timeout=5
        )

        if response.status_code == 200:
            try:
                content = response.json().get('quoteText')
                if content:
                    quote_details['quote'] = content
                    quote_details['author'] = response.json().get('quoteAuthor')
                    quote_details['length'] = len(content)
                    return quote_details
            except requests.exceptions.JSONDecodeError as e:
                print(f"Second source is out: {e}")

        # third source (stoic quotes)
        response = requests.get(
            "https://stoic.tekloon.net/stoic-quote",
            timeout=5,
            verify=False
        )

        if response.status_code == 200:
            content = response.json().get('data').get('quote')
            if content:
                quote_details['quote'] = content
                quote_details['author'] = response.json().get('data').get('author')
                quote_details['length'] = len(content)
                return quote_details

            raise KeyError('Content empty')


def generate_image():
    template_path = "images/dark_quote_template_no_text.jpg"
    output_path = "images/output.jpg"
    quote_details = get_quote()

    if not quote_details.get("quote"):
        return Exception("No quote")

    # load image
    img = Image.open(template_path).convert("RGB")
    draw = ImageDraw.Draw(img)

    # load fonts
    font_path = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
    quote_font = ImageFont.truetype(font_path, 48)
    author_font = ImageFont.truetype(font_path, 32)

    # image size
    img_width, img_height = img.size
    # max_width = img_width - 100

    wrapped_text = textwrap.fill(quote_details['quote'], width=40)

    quote_lines = wrapped_text.split("\n")
    line_height = quote_font.getbbox("A")[3] + 10
    total_height = len(quote_lines) + line_height + 60  # 60 extra for spacing + author

    # Measure heights
    quote_block_height = len(quote_lines) * line_height
    author_height = author_font.getbbox("A")[3]
    padding_between = 20
    total_text_height = quote_block_height + author_height + padding_between

    if total_text_height > img_height - 100:
        print("❌ Text block exceeds image height! Consider resizing font or trimming text.")
        raise Exception("Text block exceeds image height! Consider resizing font or trimming text.")

    # vertical positioning
    y_start = (img_height - total_height) // 2

    # draw each quote line
    for line in quote_lines:
        line_width = quote_font.getlength(line)
        x = (img_width - line_width) // 2
        draw.text((x, y_start), line, font=quote_font, fill="white")
        y_start += line_height

    # draw quote author
    author_text = f"- {quote_details['author']}"
    author_width = author_font.getlength(author_text)
    x = (img_width - author_width) // 2
    draw.text((x, y_start + 20), author_text, font=author_font, fill="white")

    # save output
    img.save(output_path)
    print(f"Saved to {output_path}")
    return output_path


def upload_quote_image_to_inst():
    image_path = generate_image()

    # login
    cl = Client()
    cl.load_settings(SESSION_PATH)

    cl.login(username=USERNAME, password=PASSWORD)

    # upload
    cl.photo_upload(
        path=image_path,
        caption="Invinsible"
    )
    print("finished")


upload_quote_image_to_inst()
