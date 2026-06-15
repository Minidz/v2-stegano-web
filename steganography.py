from io import BytesIO
from typing import Tuple

from PIL import Image


def _text_to_bits(text: str) -> str:
    return ''.join(f"{byte:08b}" for byte in text.encode("utf-8"))


def _bits_to_text(bits: str) -> str:
    bytes_chunk = [bits[i : i + 8] for i in range(0, len(bits), 8)]
    data = bytes(int(chunk, 2) for chunk in bytes_chunk)
    return data.decode("utf-8", errors="replace")


def _int_to_bits(value: int, length: int = 32) -> str:
    return f"{value:0{length}b}"


def _bits_to_int(bits: str) -> int:
    return int(bits, 2)


def _image_to_channel_list(image: Image.Image) -> list[int]:
    return [channel for pixel in image.getdata() for channel in pixel]


def _channel_list_to_image(channels: list[int], size: Tuple[int, int]) -> Image.Image:
    pixels = [tuple(channels[i : i + 3]) for i in range(0, len(channels), 3)]
    image = Image.new("RGB", size)
    image.putdata(pixels)
    return image


def encode_message_into_image(cover_image_bytes: bytes, message: str) -> bytes:
    image = Image.open(BytesIO(cover_image_bytes)).convert("RGB")
    width, height = image.size
    channels = _image_to_channel_list(image)

    payload_bits = _text_to_bits(message)
    message_length_bits = _int_to_bits(len(payload_bits), length=32)
    all_bits = message_length_bits + payload_bits

    capacity = len(channels)
    if len(all_bits) > capacity:
        max_bytes = (capacity - 32) // 8
        raise ValueError(
            f"Message too large for this image. Maximum message size is {max_bytes} bytes."
        )

    encoded_channels = channels.copy()
    for i, bit in enumerate(all_bits):
        encoded_channels[i] = (encoded_channels[i] & ~1) | int(bit)

    stego_image = _channel_list_to_image(encoded_channels, (width, height))
    output = BytesIO()
    stego_image.save(output, format="PNG")
    return output.getvalue()


def decode_message_from_image(stego_image_bytes: bytes) -> str:
    image = Image.open(BytesIO(stego_image_bytes)).convert("RGB")
    channels = _image_to_channel_list(image)

    if len(channels) < 32:
        raise ValueError("Image is too small to contain a hidden message.")

    length_bits = "".join(str(channels[i] & 1) for i in range(32))
    payload_length = _bits_to_int(length_bits)

    if payload_length < 0 or payload_length > len(channels) - 32:
        raise ValueError("Hidden message length is invalid or corrupted.")

    message_bits = "".join(
        str(channels[i] & 1) for i in range(32, 32 + payload_length)
    )
    return _bits_to_text(message_bits)
