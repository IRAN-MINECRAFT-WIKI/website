"""
uploader.py — دانلود تصاویر و فایل‌های ماد + آپلود به HuggingFace

🎯 کار:
1. تصویر کاور (thumbnail) رو از MCPEDL دانلود می‌کنه
2. اسکرین‌شات‌های گالری رو دانلود می‌کنه
3. فایل ماد (.mcpack/.mcaddon) رو دانلود می‌کنه
4. همه رو به HuggingFace آپلود می‌کنه (به‌همون پوشه‌بندی)
5. URL‌های HuggingFace رو برمی‌گردونه (به‌جای URLهای MCPEDL)

اینطوری سایت وابسته به MCPEDL نیست — فایل‌ها روی HuggingFace هستن.
"""
import os
import re
import requests
import urllib.parse
from pathlib import Path
from typing import Optional, Tuple

try:
    from huggingface_hub import HfApi, CommitOperationAdd
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False


def download_file(url: str, save_path: Path, referer: str = "https://mcpedl.com/") -> Optional[Path]:
    """دانلود یه فایل از URL"""
    try:
        r = requests.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Referer": referer,
            },
            timeout=60,
            stream=True,
        )
        if r.status_code != 200:
            return None
        
        # Detect file extension from Content-Type
        content_type = r.headers.get("Content-Type", "").lower()
        ext_map = {
            "image/png": ".png", "image/jpeg": ".jpg", "image/jpg": ".jpg",
            "image/webp": ".webp", "image/gif": ".gif", "image/avif": ".avif",
            "application/zip": ".zip",
            "application/octet-stream": "",
        }
        ext = ext_map.get(content_type, "")
        
        # If no ext from content-type, get from URL
        if not ext:
            url_path = url.split("?")[0].lower()
            for e in [".gif", ".png", ".jpg", ".jpeg", ".webp", ".avif", ".mcpack", ".mcaddon", ".mcworld", ".zip"]:
                if url_path.endswith(e):
                    ext = e
                    break
        
        # If still no ext, try from magic bytes
        if not ext:
            first_bytes = next(r.iter_content(1024), b"")
            if first_bytes[:8] == b'\x89PNG\r\n\x1a\n':
                ext = ".png"
            elif first_bytes[:3] == b'\xff\xd8\xff':
                ext = ".jpg"
            elif first_bytes[:6] in (b'GIF87a', b'GIF89a'):
                ext = ".gif"
            elif first_bytes[:4] == b'RIFF' and len(first_bytes) > 12 and first_bytes[8:12] == b'WEBP':
                ext = ".webp"
            else:
                ext = ".bin"
            
            # Save first bytes + rest
            save_path.parent.mkdir(parents=True, exist_ok=True)
            with open(str(save_path) + ext, "wb") as f:
                f.write(first_bytes)
                for chunk in r.iter_content(8192):
                    f.write(chunk)
            return Path(str(save_path) + ext)
        
        save_path.parent.mkdir(parents=True, exist_ok=True)
        final_path = Path(str(save_path) + ext)
        with open(final_path, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
        
        return final_path
    
    except Exception as e:
        print(f"  [uploader] Download error: {e}")
        return None


def upload_to_huggingface(
    slug: str,
    file_path: Path,
    hf_token: str,
    hf_repo_id: str = "Habib91700/minebed-mods_",
) -> Optional[str]:
    """آپلود یه فایل به HuggingFace Dataset — به پوشه‌ی slug/"""
    if not HF_AVAILABLE or not hf_token:
        return None
    
    try:
        api = HfApi()
        
        # Ensure repo exists
        try:
            api.repo_info(repo_id=hf_repo_id, repo_type="dataset", token=hf_token)
        except:
            api.create_repo(repo_id=hf_repo_id, repo_type="dataset", token=hf_token, private=False, exist_ok=True)
        
        # Upload file
        filename = file_path.name
        path_in_repo = f"{slug}/{filename}"
        
        api.upload_file(
            path_or_fileobj=str(file_path),
            path_in_repo=path_in_repo,
            repo_id=hf_repo_id,
            repo_type="dataset",
            token=hf_token,
        )
        
        # Return public URL
        safe_name = urllib.parse.quote(filename)
        url = f"https://huggingface.co/datasets/{hf_repo_id}/resolve/main/{slug}/{safe_name}"
        return url
    
    except Exception as e:
        print(f"  [uploader] HF upload error: {e}")
        return None


def process_mod_assets(
    mod_data: dict,
    hf_token: str,
    hf_repo_id: str = "Habib91700/minebed-mods_",
    cache_dir: Path = Path("cache"),
) -> dict:
    """
    دانلود + آپلود همه‌ی assets یک ماد.
    
    Returns: mod_data با URL‌های HuggingFace جایگزین‌شده
    """
    slug = mod_data.get("slug") or mod_data.get("id", "unknown")
    cache = cache_dir / slug
    cache.mkdir(parents=True, exist_ok=True)
    
    updated = mod_data.copy()
    
    # 1. Download + upload cover (thumbnail)
    cover_url = mod_data.get("cover", "")
    if cover_url and cover_url.startswith("http"):
        print(f"  [uploader] دانلود کاور...")
        cover_path = download_file(cover_url, cache / "cover")
        if cover_path:
            print(f"  [uploader] آپلود کاور به HF...")
            hf_url = upload_to_huggingface(slug, cover_path, hf_token, hf_repo_id)
            if hf_url:
                updated["cover"] = hf_url
                print(f"  [uploader] ✅ کاور: {hf_url[:60]}...")
    
    # 2. Download + upload gallery images
    gallery = mod_data.get("gallery", [])
    new_gallery = []
    for i, img_url in enumerate(gallery[:8]):
        if img_url and img_url.startswith("http"):
            print(f"  [uploader] دانلود گالری {i+1}...")
            img_path = download_file(img_url, cache / f"screenshot_{i+1}")
            if img_path:
                hf_url = upload_to_huggingface(slug, img_path, hf_token, hf_repo_id)
                if hf_url:
                    new_gallery.append(hf_url)
                    print(f"  [uploader] ✅ گالری {i+1}")
                else:
                    new_gallery.append(img_url)  # fallback to original
            else:
                new_gallery.append(img_url)  # fallback
        else:
            new_gallery.append(img_url)
    updated["gallery"] = new_gallery
    
    # 3. Download + upload mod files (.mcpack / .mcaddon / .mcworld)
    files = mod_data.get("files", [])
    new_download_url = updated.get("downloadUrl", "")
    
    if files:
        first_file_url = files[0] if isinstance(files[0], str) else files[0].get("href", "")
        if first_file_url and first_file_url.startswith("http"):
            print(f"  [uploader] دانلود فایل ماد...")
            mod_path = download_file(first_file_url, cache / f"{slug}")
            if mod_path:
                print(f"  [uploader] آپلود فایل ماد به HF...")
                hf_url = upload_to_huggingface(slug, mod_path, hf_token, hf_repo_id)
                if hf_url:
                    new_download_url = hf_url
                    print(f"  [uploader] ✅ فایل ماد: {hf_url[:60]}...")
    
    if new_download_url:
        updated["downloadUrl"] = new_download_url
    
    # Cleanup cache
    import shutil
    try:
        shutil.rmtree(cache)
    except:
        pass
    
    return updated
