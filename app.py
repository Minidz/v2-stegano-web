import io
import os
from pathlib import Path
from typing import Union, Tuple

import gradio as gr
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse, RedirectResponse, StreamingResponse
from gradio import mount_gradio_app

from PIL import Image
import numpy as np
import torch
from torchvision import transforms
import zlib
from collections import Counter

try:
    from reedsolo import RSCodec
    REEDSOLO_AVAILABLE = True
except ImportError:
    RSCodec = None
    REEDSOLO_AVAILABLE = False

from models import DenseDecoder, DenseEncoder

# Configuration (match app.py behaviour)
DATA_DEPTH = 4
HIDDEN_SIZE = 32
MIN_SIZE = 128
MAX_SIZE = int(os.environ.get("MAX_IMAGE_SIZE", "512"))
MODEL_PATH = Path(__file__).parent / "models/model_GAN/endecode_GAN.pt"
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
THRESHOLD = 0.5
TORCH_NUM_THREADS = int(os.environ.get("TORCH_NUM_THREADS", "1"))
torch.set_num_threads(TORCH_NUM_THREADS)

app = FastAPI(
    title="Steganography Demo API",
    description="Upload an image to encode a secret message or decode a hidden message from an image.",
)
UI_PATH = "/ui"

encoder = None
decoder = None
rs = None


def _get_closest_valid_size(width: int, height: int) -> Tuple[int, int]:
    max_dim = min(max(width, height), MAX_SIZE)
    adjusted_size = max_dim - (max_dim % 8)
    adjusted_size = max(adjusted_size, MIN_SIZE)
    return adjusted_size, adjusted_size


def _image_to_tensor(image: Image.Image) -> torch.Tensor:
    image = image.convert("RGB")
    width, height = image.size
    target_width, target_height = _get_closest_valid_size(width, height)

    transform = transforms.Compose([
        transforms.Resize([target_height, target_width]),
        transforms.ToTensor(),
        transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])
    ])
    tensor = transform(image).unsqueeze(0)
    return tensor


def _tensor_to_image(tensor: torch.Tensor) -> Image.Image:
    tensor = tensor.clone().detach().cpu().squeeze(0)
    tensor = (tensor * 0.5) + 0.5
    tensor = tensor.clamp(0, 1)
    return transforms.ToPILImage()(tensor)


def _load_image_bytes(image_bytes: bytes) -> Image.Image:
    try:
        return Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Unable to load uploaded image: {exc}")


def bytearray_to_bits(x: bytearray) -> list[int]:
    result = []
    for i in x:
        bits = bin(i)[2:]
        bits = "00000000"[len(bits):] + bits
        result.extend([int(b) for b in bits])
    return result


def bits_to_bytearray(bits: list[int]) -> bytearray:
    ints = []
    for b in range(len(bits) // 8):
        byte = bits[b * 8:(b + 1) * 8]
        ints.append(int("".join(str(bit) for bit in byte), 2))
    return bytearray(ints)


def text_to_bytearray(text: str) -> bytearray:
    assert isinstance(text, str), "expected a string"
    compressed = zlib.compress(text.encode("utf-8"))
    if REEDSOLO_AVAILABLE:
        compressed = rs.encode(bytearray(compressed))
    return bytearray(compressed)


def bytearray_to_text(x: bytearray) -> Union[str, bool]:
    try:
        if REEDSOLO_AVAILABLE:
            decoded = rs.decode(x)[0]
        else:
            decoded = bytes(x)
        decompressed = zlib.decompress(decoded)
        return decompressed.decode("utf-8")
    except Exception:
        return False


def text_to_bits(text: str) -> list[int]:
    return bytearray_to_bits(text_to_bytearray(text))


def bits_to_text(bits: list[int]) -> str:
    try:
        text = bytearray_to_text(bits_to_bytearray(bits))
        return text if text is not False else ""
    except Exception:
        return ""


def make_payload(width: int, height: int, depth: int, text: str) -> torch.Tensor:
    message = text_to_bits(text) + [0] * 32
    payload = message
    while len(payload) < width * height * depth:
        payload += message
    payload = payload[: width * height * depth]
    return torch.FloatTensor(payload).view(1, depth, height, width)


def make_message_from_bits(bits: list[int]) -> str:
    candidates = Counter()
    byte_data = bits_to_bytearray(bits)
    for candidate in byte_data.split(b"\x00\x00\x00\x00"):
        text = bytearray_to_text(bytearray(candidate))
        if text:
            candidates[text] += 1
    if len(candidates) == 0:
        return ""
    return candidates.most_common(1)[0][0]


def load_models() -> None:
    global encoder, decoder, rs

    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")

    encoder = DenseEncoder(DATA_DEPTH, HIDDEN_SIZE).to(DEVICE)
    decoder = DenseDecoder(DATA_DEPTH, HIDDEN_SIZE).to(DEVICE)

    states = torch.load(MODEL_PATH, map_location=DEVICE)
    if "state_dict_encoder" not in states or "state_dict_decoder" not in states:
        raise ValueError("Pretrained model state does not contain expected keys.")

    encoder.load_state_dict(states["state_dict_encoder"])
    decoder.load_state_dict(states["state_dict_decoder"])
    encoder.eval()
    decoder.eval()

    if REEDSOLO_AVAILABLE:
        rs = RSCodec(250)


@app.on_event("startup")
async def startup_event() -> None:
    load_models()


@app.get("/", include_in_schema=False)
async def root() -> RedirectResponse:
    return RedirectResponse(url=UI_PATH)


@app.post("/encode")
async def encode(cover_image: UploadFile = File(...), message: str = Form(...)):
    if cover_image.content_type not in {"image/png", "image/jpeg", "image/jpg"}:
        raise HTTPException(
            status_code=400,
            detail="Upload a PNG or JPEG image file for cover image.",
        )

    image_bytes = await cover_image.read()
    pil_image = _load_image_bytes(image_bytes)
    image_tensor = _image_to_tensor(pil_image).to(DEVICE)
    _, _, height, width = image_tensor.shape

    payload = make_payload(width, height, DATA_DEPTH, message).to(DEVICE)
    with torch.inference_mode():
        stego_tensor = encoder(image_tensor, payload)

    # Optional: preserve global color by removing per-channel residual mean
    def _preserve_color(cover: torch.Tensor, stego: torch.Tensor) -> torch.Tensor:
        # cover/stego: (1, 3, H, W)
        residual = stego - cover
        mean = residual.mean(dim=(2, 3), keepdim=True)
        residual = residual - mean
        corrected = cover + residual
        return corrected.clamp(-1.0, 1.0)

    stego_tensor = _preserve_color(image_tensor, stego_tensor)

    stego_image = _tensor_to_image(stego_tensor)
    buffer = io.BytesIO()
    stego_image.save(buffer, format="PNG")
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="image/png",
        headers={"Content-Disposition": "attachment; filename=stego.png"}
    )


@app.post("/decode")
async def decode(stego_image: UploadFile = File(...)) -> JSONResponse:
    if stego_image.content_type not in {"image/png", "image/jpeg", "image/jpg"}:
        raise HTTPException(
            status_code=400,
            detail="Upload a PNG or JPEG image file for stego image.",
        )

    image_bytes = await stego_image.read()
    pil_image = _load_image_bytes(image_bytes)
    image_tensor = _image_to_tensor(pil_image).to(DEVICE)

    with torch.inference_mode():
        decoded_payload = decoder(image_tensor)

    bits = (decoded_payload.view(-1) > THRESHOLD).cpu().numpy().astype(np.uint8).tolist()
    text = make_message_from_bits(bits)
    if text == "":
        text = bits_to_text(bits)

    return JSONResponse({
        "success": True,
        "decoded_message": text,
        "message_length": len(text)
    })


def _read_bytes_from_input(file: Union[str, object]) -> bytes:
    if file is None:
        raise ValueError("No file provided")
    if isinstance(file, str):
        return Path(file).read_bytes()
    if hasattr(file, "name"):
        return Path(file.name).read_bytes()
    raise ValueError("Unsupported file input format")


def _gradio_encode(file, message):
    image_bytes = _read_bytes_from_input(file)
    pil_image = _load_image_bytes(image_bytes)
    image_tensor = _image_to_tensor(pil_image).to(DEVICE)
    _, _, height, width = image_tensor.shape
    payload = make_payload(width, height, DATA_DEPTH, message).to(DEVICE)
    with torch.inference_mode():
        stego_tensor = encoder(image_tensor, payload)

    # preserve color like API endpoint
    def _preserve_color(cover: torch.Tensor, stego: torch.Tensor) -> torch.Tensor:
        residual = stego - cover
        mean = residual.mean(dim=(2, 3), keepdim=True)
        residual = residual - mean
        corrected = cover + residual
        return corrected.clamp(-1.0, 1.0)

    stego_tensor = _preserve_color(image_tensor, stego_tensor)
    stego_image = _tensor_to_image(stego_tensor)
    temp_path = Path("stego_output.png")
    buf = io.BytesIO()
    stego_image.save(buf, format="PNG")
    temp_path.write_bytes(buf.getvalue())
    return str(temp_path)


def _gradio_decode(file):
    image_bytes = _read_bytes_from_input(file)
    pil_image = _load_image_bytes(image_bytes)
    image_tensor = _image_to_tensor(pil_image).to(DEVICE)
    with torch.inference_mode():
        decoded_payload = decoder(image_tensor)
    bits = (decoded_payload.view(-1) > THRESHOLD).cpu().numpy().astype(np.uint8).tolist()
    text = make_message_from_bits(bits)
    if text == "":
        text = bits_to_text(bits)
    return text


demo = gr.Blocks()
with demo:
    gr.Markdown("# Steganography Demo UI")
    gr.Markdown("Upload a cover image to hide text, or upload a stego image to decode hidden text.")

    with gr.Tab("Encode"):
        cover_input = gr.Image(type="filepath", label="Cover Image")
        message_input = gr.Textbox(label="Secret message", lines=4, placeholder="Enter text to hide")
        encode_button = gr.Button("Encode")
        stego_output = gr.File(label="Download stego image")
        encode_button.click(_gradio_encode, [cover_input, message_input], stego_output)

    with gr.Tab("Decode"):
        stego_input = gr.Image(type="filepath", label="Stego Image")
        decode_button = gr.Button("Decode")
        decoded_output = gr.Textbox(label="Hidden message")
        decode_button.click(_gradio_decode, stego_input, decoded_output)


mount_gradio_app(app, demo, path=UI_PATH)


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)
