# Deploy len Hugging Face Spaces

Khuyen dung cach nay cho project hien tai: tao Space kieu Docker. App se chay `app.py`, co FastAPI docs o `/docs` va giao dien Gradio o `/ui`.

## 1. Kiem tra file can co

Dam bao repo co cac file/folder sau:

```text
app.py
Dockerfile
requirements.txt
models/
models/model_GAN/endecode_GAN.pt
steganography.py
steganography_gan.py
```

## 2. Tao Space tren Hugging Face

1. Vao https://huggingface.co/spaces
2. Chon **Create new Space**
3. Dat ten Space
4. Chon **SDK: Docker**
5. Chon visibility Public hoac Private
6. Tao Space

## 3. Push code len Space

Copy URL git cua Space, sau do push repo len:

```bash
git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME
git push hf main
```

Neu branch cua ban la `master`:

```bash
git push hf master:main
```

## 4. Mo app

Sau khi build xong, mo:

```text
https://YOUR_USERNAME-YOUR_SPACE_NAME.hf.space/
https://YOUR_USERNAME-YOUR_SPACE_NAME.hf.space/ui
https://YOUR_USERNAME-YOUR_SPACE_NAME.hf.space/docs
```

Root `/` se tu redirect sang `/ui`.

## 5. Loi hay gap

### Model file not found

Kiem tra file nay da duoc push len Space:

```text
models/model_GAN/endecode_GAN.pt
```

### Build qua cham hoac loi cai torch

Torch va torchvision kha nang, nen lan build dau co the mat nhieu phut. Neu bi loi do thieu RAM/disk tren free tier, hay thu restart Space hoac dung Space co tai nguyen cao hon.

### App co `/docs` nhung khong thay UI

Mo truc tiep `/ui`. Project da cau hinh `/` redirect sang `/ui`.

