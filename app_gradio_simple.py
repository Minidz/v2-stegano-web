import io
import gradio as gr
from PIL import Image
from steganography_gan import encode_message_into_image, decode_message_from_image


def encode_interface(cover_image, secret_message):
    """Encode secret message into cover image"""
    if cover_image is None:
        return None, "❌ Vui lòng upload ảnh"

    if not secret_message or secret_message.strip() == "":
        return None, "❌ Vui lòng nhập tin nhắn"

    try:
        # Convert PIL Image to bytes
        img_byte_arr = io.BytesIO()
        cover_image.save(img_byte_arr, format="PNG")
        cover_bytes = img_byte_arr.getvalue()

        # Encode
        stego_bytes = encode_message_into_image(cover_bytes, secret_message)

        # Convert back to PIL Image for display
        stego_image = Image.open(io.BytesIO(stego_bytes))

        return stego_image, f"✅ Ẩn tin nhắn thành công!\nDộ dài: {len(secret_message)} ký tự"
    except Exception as e:
        return None, f"❌ Lỗi: {str(e)}"


def decode_interface(stego_image):
    """Decode secret message from stego image"""
    if stego_image is None:
        return "❌ Vui lòng upload ảnh"

    try:
        # Convert PIL Image to bytes
        img_byte_arr = io.BytesIO()
        stego_image.save(img_byte_arr, format="PNG")
        stego_bytes = img_byte_arr.getvalue()

        # Decode
        message = decode_message_from_image(stego_bytes)

        return f"✅ Giải mã thành công!\n\n📝 Tin nhắn:\n{message}"
    except Exception as e:
        return f"❌ Lỗi: {str(e)}"


# Create Gradio interface
with gr.Blocks(title="🔐 Steganography Demo", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🔐 Ẩn tin nhắn trong ảnh (Steganography)")
    gr.Markdown(
        "Ứng dụng sử dụng phương pháp **LSB (Least Significant Bit)** để ẩn và giải mã tin nhắn từ ảnh"
    )
    gr.Markdown("---")

    with gr.Tabs():
        # Encode tab
        with gr.TabItem("🔒 Ẩn tin nhắn", id="encode"):
            gr.Markdown("### 📸 Upload ảnh gốc và nhập tin nhắn để ẩn")
            with gr.Row():
                with gr.Column(scale=1):
                    encode_image = gr.Image(
                        label="Ảnh gốc (Cover)", type="pil", format="png"
                    )
                    encode_message = gr.Textbox(
                        label="Tin nhắn cần ẩn",
                        placeholder="Nhập tin nhắn...",
                        lines=4,
                    )
                    encode_btn = gr.Button("🔒 Ẩn tin nhắn", variant="primary", size="lg")

                with gr.Column(scale=1):
                    encode_output_image = gr.Image(
                        label="Ảnh có chứa tin nhắn (Stego)", type="pil"
                    )
                    encode_status = gr.Textbox(label="Trạng thái", interactive=False)

            encode_btn.click(
                fn=encode_interface,
                inputs=[encode_image, encode_message],
                outputs=[encode_output_image, encode_status],
            )

        # Decode tab
        with gr.TabItem("🔓 Giải mã tin nhắn", id="decode"):
            gr.Markdown("### 🖼️ Upload ảnh chứa tin nhắn để giải mã")
            with gr.Row():
                with gr.Column(scale=1):
                    decode_image = gr.Image(
                        label="Ảnh có chứa tin nhắn (Stego)", type="pil", format="png"
                    )
                    decode_btn = gr.Button("🔓 Giải mã", variant="primary", size="lg")

                with gr.Column(scale=1):
                    decode_output = gr.Textbox(
                        label="Kết quả giải mã", interactive=False, lines=8
                    )

            decode_btn.click(
                fn=decode_interface,
                inputs=[decode_image],
                outputs=[decode_output],
            )

    gr.Markdown("---")
    gr.Markdown(
        """
    ## 📖 Hướng dẫn sử dụng

    ### 🔒 Tab "Ẩn tin nhắn":
    1. Chọn **ảnh gốc** (PNG hoặc JPEG)
    2. Nhập **tin nhắn** muốn ẩn
    3. Nhấp **"Ẩn tin nhắn"**
    4. Tải ảnh kết quả chứa tin nhắn ẩn

    ### 🔓 Tab "Giải mã":
    1. Chọn **ảnh có chứa tin nhắn**
    2. Nhấp **"Giải mã"**
    3. Xem **kết quả** (tin nhắn giải mã)

    ## ⚠️ Lưu ý quan trọng:
    - **Kích thước ảnh**: Ảnh càng lớn, tin nhắn càng dài có thể ẩn (tối thiểu ~256×256)
    - **Định dạng**: Hỗ trợ PNG, JPEG
    - **Độ bí mật**: Ảnh ẩn gần như không khác so với ảnh gốc
    - **Lỗi dữ liệu**: Nếu ảnh bị nén hay sửa đổi, tin nhắn có thể mất

    ## 🔐 Bảo mật:
    - Đây là demo giáo dục đơn giản (LSB cơ bản)
    - Trong thực tế, nên kết hợp với mã hóa (AES, RSA) để bảo vệ tin nhắn
    """
    )


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)
