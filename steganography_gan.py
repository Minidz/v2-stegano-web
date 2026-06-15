import io
import zlib
import torch
import torch.nn as nn
from PIL import Image
import numpy as np
from pathlib import Path
from reedsolo import RSCodec


# ============================================================================
# MODEL ARCHITECTURE (Dựa trên endecode_GAN.pt)
# ============================================================================

class DenseEncoder(nn.Module):
    def __init__(self, data_depth=4, hidden=32):
        super().__init__()
        self.data_depth = data_depth
        self.hidden = hidden
        
        # Input: 3 channels (RGB) + data_depth = 3 + 4 = 7 channels
        # Output: 3 channels (RGB)
        self.conv1 = nn.Sequential(
            nn.Conv2d(3, hidden, 3, padding=1),
            nn.LeakyReLU(inplace=True),
            nn.BatchNorm2d(hidden),
        )
        
        self.conv2 = nn.Sequential(
            nn.Conv2d(hidden + data_depth, hidden, 3, padding=1),
            nn.LeakyReLU(inplace=True),
            nn.BatchNorm2d(hidden),
        )
        
        self.conv3 = nn.Sequential(
            nn.Conv2d(hidden * 2 + data_depth, hidden, 3, padding=1),
            nn.LeakyReLU(inplace=True),
            nn.BatchNorm2d(hidden),
        )
        
        self.conv4 = nn.Sequential(
            nn.Conv2d(hidden * 3 + data_depth, 3, 3, padding=1),
        )
    
    def forward(self, image, data):
        # image: (B, 3, H, W)
        # data: (B, data_depth, H, W)
        
        out1 = self.conv1(image)
        x1 = torch.cat([out1, data], dim=1)
        
        out2 = self.conv2(x1)
        x2 = torch.cat([out2, out1, data], dim=1)
        
        out3 = self.conv3(x2)
        x3 = torch.cat([out3, out2, out1, data], dim=1)
        
        output = self.conv4(x3)
        return image + output


class DenseDecoder(nn.Module):
    def __init__(self, data_depth=4, hidden=32):
        super().__init__()
        self.data_depth = data_depth
        self.hidden = hidden
        
        self.conv1 = nn.Sequential(
            nn.Conv2d(3, hidden, 3, padding=1),
            nn.LeakyReLU(inplace=True),
            nn.BatchNorm2d(hidden),
        )
        
        self.conv2 = nn.Sequential(
            nn.Conv2d(hidden, hidden, 3, padding=1),
            nn.LeakyReLU(inplace=True),
            nn.BatchNorm2d(hidden),
        )
        
        self.conv3 = nn.Sequential(
            nn.Conv2d(hidden * 2, hidden, 3, padding=1),
            nn.LeakyReLU(inplace=True),
            nn.BatchNorm2d(hidden),
        )
        
        self.conv4 = nn.Sequential(
            nn.Conv2d(hidden * 3, data_depth, 3, padding=1),
        )
    
    def forward(self, image):
        # image: (B, 3, H, W)
        # output: (B, data_depth, H, W)
        
        out1 = self.conv1(image)
        out2 = self.conv2(out1)
        x2 = torch.cat([out2, out1], dim=1)
        
        out3 = self.conv3(x2)
        x3 = torch.cat([out3, out2, out1], dim=1)
        
        output = self.conv4(x3)
        return output


# ============================================================================
# HELPERS
# ============================================================================

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
MODEL_PATH = Path(__file__).parent / "endecode_GAN_F.pt"

# Reed-Solomon error correction matches the reference notebook's payload pipeline
rs = RSCodec(250)

# Decoder thresholds borrowed from demo.py for better recovery
THRESHOLDS = [0.5, 0.45, 0.55, 0.4, 0.6, 0.35, 0.65, 0.3, 0.7]

# Load model globally
_encoder = None
_decoder = None


def _load_model():
    global _encoder, _decoder
    
    if _encoder is None or _decoder is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")
        
        print(f"Loading GAN model from {MODEL_PATH}...")
        
        checkpoint = torch.load(MODEL_PATH, map_location=DEVICE)
        
        # Reconstruct models
        encoder = DenseEncoder(data_depth=4, hidden=32).to(DEVICE)
        decoder = DenseDecoder(data_depth=4, hidden=32).to(DEVICE)
        
        encoder.load_state_dict(checkpoint["state_dict_encoder"])
        decoder.load_state_dict(checkpoint["state_dict_decoder"])
        
        encoder.eval()
        decoder.eval()
        
        _encoder = encoder
        _decoder = decoder
        
        print("Model loaded successfully!")


def _text_to_bytearray(text: str) -> bytearray:
    """Compress text and add Reed-Solomon error correction."""
    assert isinstance(text, str), "expected a string"
    compressed = zlib.compress(text.encode("utf-8"))
    return rs.encode(bytearray(compressed))


def _bytearray_to_text(x: bytearray) -> str:
    """Decode Reed-Solomon data and decompress text."""
    try:
        decoded = rs.decode(x)[0]
        decompressed = zlib.decompress(decoded)
        return decompressed.decode("utf-8")
    except Exception:
        raise ValueError("Failed to decode message payload")


def _text_to_bits(text: str) -> list[int]:
    """Convert text to a list of bits after compression and error correction."""
    data = _text_to_bytearray(text)
    bits: list[int] = []
    for byte in data:
        bits.extend(int(bit) for bit in f"{byte:08b}")
    return bits


def _bits_to_text(bits: list[int]) -> str:
    """Convert a list of bits back to text using Reed-Solomon and decompression."""
    if len(bits) % 8 != 0:
        raise ValueError("Bit stream length must be a multiple of 8")
    raw = bytearray()
    for i in range(0, len(bits), 8):
        raw.append(int(''.join(str(b) for b in bits[i : i + 8]), 2))
    return _bytearray_to_text(raw)


def _image_to_tensor(image_bytes: bytes, size: int = 256) -> torch.Tensor:
    """Convert image bytes to normalized tensor"""
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img = img.resize((size, size), Image.Resampling.LANCZOS)
    
    img_array = np.array(img).astype(np.float32) / 127.5 - 1.0  # Normalize to [-1, 1]
    img_tensor = torch.from_numpy(img_array).permute(2, 0, 1).unsqueeze(0).to(DEVICE)
    
    return img_tensor


def _tensor_to_image(tensor: torch.Tensor) -> bytes:
    """Convert tensor to image bytes"""
    with torch.no_grad():
        img_array = tensor.squeeze(0).permute(1, 2, 0).cpu().numpy()
        img_array = np.clip((img_array + 1.0) * 127.5, 0, 255).astype(np.uint8)
        img = Image.fromarray(img_array, mode="RGB")
    
    output = io.BytesIO()
    img.save(output, format="PNG")
    return output.getvalue()


def _message_to_data_tensor(message: str, height: int, width: int) -> torch.Tensor:
    """Convert message to 4-channel data tensor using RS-protected payload and zero padding."""
    payload_bits = _text_to_bits(message) + [0] * 32
    total_bits = height * width * 4

    if len(payload_bits) > total_bits:
        raise ValueError(f"Message too long! Max {total_bits // 8} bytes for {height}x{width} image")

    # Fill the payload once then pad with zeros for the remaining capacity.
    payload = payload_bits + [0] * (total_bits - len(payload_bits))
    payload = payload[:total_bits]

    data_array = np.array(payload, dtype=np.float32).reshape((4, height, width))
    return torch.from_numpy(data_array).unsqueeze(0).to(DEVICE)


def _data_tensor_to_message(data_tensor: torch.Tensor) -> str:
    """Convert 4-channel data tensor back to a decoded text message."""
    with torch.no_grad():
        data_array = data_tensor.squeeze(0).cpu().numpy()

    height, width = data_array.shape[1:]
    total_bits = height * width * 4

    candidates: dict[str, int] = {}
    raw_bytes = None

    for threshold in THRESHOLDS:
        bits: list[int] = []
        for c in range(4):
            for i in range(height * width):
                bits.append(1 if data_array[c, i // width, i % width] > threshold else 0)

        raw_bytes = bytearray()
        for i in range(0, len(bits), 8):
            raw_bytes.append(int(''.join(str(b) for b in bits[i : i + 8]), 2))

        for pattern in [b'\x00\x00\x00\x00', b'\x00\x00\x00', b'\x00\x00', b'\x00']:
            for segment in raw_bytes.split(pattern):
                if len(segment) < 10:
                    continue
                try:
                    candidate = _bytearray_to_text(bytearray(segment))
                    if candidate:
                        candidates[candidate] = candidates.get(candidate, 0) + 1
                        if candidates[candidate] >= 3:
                            return candidate
                except ValueError:
                    continue

    if len(candidates) == 0 and raw_bytes is not None:
        # Final fallback: try decode from the full raw byte stream.
        try:
            return _bytearray_to_text(raw_bytes)
        except ValueError:
            pass

    if not candidates:
        raise ValueError("Failed to decode message from stego tensor")

    return max(candidates.items(), key=lambda x: x[1])[0]


# ============================================================================
# PUBLIC API
# ============================================================================

def encode_message_into_image(cover_image_bytes: bytes, message: str) -> bytes:
    """
    Encode secret message into cover image using GAN model
    
    Args:
        cover_image_bytes: Original image bytes (PNG/JPEG)
        message: Secret message to hide
    
    Returns:
        Stego image bytes (PNG)
    """
    _load_model()
    
    # Normalize image size
    size = 256
    
    # Convert image to tensor
    cover_tensor = _image_to_tensor(cover_image_bytes, size=size)
    
    # Convert message to data tensor
    data_tensor = _message_to_data_tensor(message, size, size)
    
    # Encode using GAN
    with torch.no_grad():
        stego_tensor = _encoder(cover_tensor, data_tensor)
    
    # Convert back to image bytes
    stego_bytes = _tensor_to_image(stego_tensor)
    
    return stego_bytes


def decode_message_from_image(stego_image_bytes: bytes) -> str:
    """
    Decode secret message from stego image using GAN model
    
    Args:
        stego_image_bytes: Stego image bytes (PNG/JPEG)
    
    Returns:
        Decoded secret message
    """
    _load_model()
    
    # Normalize image size
    size = 256
    
    # Convert stego image to tensor
    stego_tensor = _image_to_tensor(stego_image_bytes, size=size)
    
    # Decode using GAN
    with torch.no_grad():
        data_tensor = _decoder(stego_tensor)
    
    # Extract message from data tensor
    message = _data_tensor_to_message(data_tensor)
    
    return message
