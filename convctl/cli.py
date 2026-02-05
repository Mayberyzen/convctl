#!/usr/bin/env python3
"""
Universal Converter CLI - Interactive Menu Edition
A comprehensive file conversion tool with interactive menu interface.
"""

import os
import sys
import argparse
import subprocess
import platform
import shutil
import glob
import io
import time
from pathlib import Path
from typing import List, Tuple, Optional

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False
    tqdm = lambda x: x

IS_LINUX = platform.system().lower() == "linux"
IS_WINDOWS = platform.system().lower() == "windows"
IS_MAC = platform.system().lower() == "darwin"


BANNER = """
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   ██████╗ ██████╗ ███╗   ██╗██╗   ██╗ ██████╗████████╗██╗        ║
║  ██╔════╝██╔═══██╗████╗  ██║██║   ██║██╔════╝╚══██╔══╝██║        ║
║  ██║     ██║   ██║██╔██╗ ██║██║   ██║██║        ██║   ██║        ║
║  ██║     ██║   ██║██║╚██╗██║██║   ██║██║        ██║   ██║        ║
║  ╚██████╗╚██████╔╝██║ ╚████║╚██████╔╝╚██████╗   ██║   ███████╗   ║
║   ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝  ╚═════╝   ╚═╝   ╚══════╝   ║
║                                                                  ║
║ Universal File Converter - v2.0 Interactive by.github/Mayberyzen ║
╚══════════════════════════════════════════════════════════════════╝
"""

def clear_screen():
    """Clear terminal screen."""
    os.system('cls' if IS_WINDOWS else 'clear')

def print_header():
    """Print banner with animation effect."""
    clear_screen()
    print(BANNER)
    print()

def which(cmd: str) -> Optional[str]:
    """Find command in system PATH."""
    return shutil.which(cmd)

def ensure_dir(path: str) -> None:
    """Ensure directory exists."""
    os.makedirs(path, exist_ok=True)

def safe_remove(path: str) -> None:
    """Safely remove file if it exists."""
    try:
        if os.path.exists(path):
            os.remove(path)
    except OSError:
        pass

def check_import(module_name: str) -> bool:
    """Check if a module can be imported without crashing."""
    import importlib.util
    spec = importlib.util.find_spec(module_name)
    return spec is not None

def get_input_file(prompt: str) -> str:
    """Get input file path with validation."""
    while True:
        filepath = input(f"{prompt}: ").strip().strip('"')
        if not filepath:
            print("❌ Please enter a file path.")
            continue
        if not os.path.exists(filepath):
            print(f"❌ File not found: {filepath}")
            continue
        return filepath

def get_output_path(input_path: str, new_ext: str) -> str:
    """Generate output path based on input."""
    inp = Path(input_path)
    # If new_ext doesn't start with dot, add it
    if not new_ext.startswith('.'):
        new_ext = '.' + new_ext
    return str(inp.with_suffix(new_ext))

def confirm_overwrite(path: str) -> bool:
    """Ask for overwrite confirmation if file exists."""
    if os.path.exists(path):
        resp = input(f"⚠️  File '{path}' exists. Overwrite? (y/n): ").lower()
        return resp in ('y', 'yes')
    return True

def doctor():
    """Check system dependencies and Python packages."""
    print_header()
    print("🔍 SYSTEM DIAGNOSTICS\n")
    
    tools = {
        "LibreOffice": which("libreoffice") or which("soffice"),
        "Pandoc": which("pandoc"),
        "Ghostscript": which("gs"),
        "FFmpeg": which("ffmpeg"),
    }
    
    python_packages = {
        "PIL (Pillow)": check_import("PIL"),
        "pypdf": check_import("pypdf"),
        "pdf2image": check_import("pdf2image"),
        "pdf2docx": check_import("pdf2docx"),
        "reportlab": check_import("reportlab"),
        "docx2pdf": check_import("docx2pdf"),
        "pywin32": check_import("win32com"),
    }
    
    print("System Dependencies:")
    print("-" * 40)
    for name, path in tools.items():
        status = f"✅ OK" if path else "❌ MISSING"
        print(f"  {name:15} {status}")
        if path:
            print(f"      └─ {path}")
    
    print("\nPython Packages:")
    print("-" * 40)
    for name, installed in python_packages.items():
        status = "✅ OK" if installed else "❌ MISSING"
        pkg = name.split()[0].lower()
        print(f"  {name:15} {status}")
        if not installed:
            print(f"      └─ pip install {pkg}")
    
    print("\nPlatform Info:")
    print("-" * 40)
    print(f"  System: {platform.system()} {platform.release()}")
    print(f"  Python: {platform.python_version()}")
    print(f"  Machine: {platform.machine()}")
    
    input("\n\nPress Enter to continue...")

def convert_docx_to_pdf_windows(inp: str, out: str) -> None:
    """Convert DOCX to PDF using docx2pdf (Windows only)."""
    try:
        from docx2pdf import convert
        convert(inp, out)
    except ImportError:
        raise RuntimeError("docx2pdf not installed. Run: pip install docx2pdf")

def convert_docx_to_pdf_linux(inp: str, out: str) -> None:
    """Convert DOCX to PDF using LibreOffice (Linux/Mac)."""
    libreoffice = which("libreoffice") or which("soffice")
    if not libreoffice:
        raise RuntimeError("LibreOffice not found. Install: sudo apt install libreoffice")
    
    outdir = os.path.dirname(os.path.abspath(out)) or "."
    basename = Path(inp).stem
    
    result = subprocess.run(
        [libreoffice, "--headless", "--convert-to", "pdf", inp, "--outdir", outdir],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        raise RuntimeError(f"LibreOffice conversion failed: {result.stderr}")
    
    generated = os.path.join(outdir, f"{basename}.pdf")
    if generated != out and os.path.exists(generated):
        shutil.move(generated, out)

def convert_docx_to_pdf(inp: str, out: str) -> None:
    """Route DOCX→PDF conversion based on platform."""
    if IS_LINUX or IS_MAC:
        convert_docx_to_pdf_linux(inp, out)
    elif IS_WINDOWS:
        convert_docx_to_pdf_windows(inp, out)
    else:
        convert_docx_to_pdf_linux(inp, out)

def convert_doc_to_pdf(inp: str, out: str) -> None:
    """Convert DOC to PDF."""
    if IS_WINDOWS:
        try:
            import win32com.client
            word = win32com.client.Dispatch("Word.Application")
            word.Visible = False
            doc = word.Documents.Open(os.path.abspath(inp))
            doc.SaveAs(os.path.abspath(out), 17)
            doc.Close()
            word.Quit()
        except ImportError:
            raise RuntimeError("pywin32 not installed. Run: pip install pywin32")
        except Exception as e:
            raise RuntimeError(f"Word automation failed: {e}")
    else:
        libreoffice = which("libreoffice") or which("soffice")
        if libreoffice:
            convert_docx_to_pdf_linux(inp, out)
        else:
            raise RuntimeError("DOC conversion requires LibreOffice on Linux/Mac")

def convert_pdf_to_docx(inp: str, out: str) -> None:
    """Convert PDF to DOCX."""
    try:
        from pdf2docx import Converter
        cv = Converter(inp)
        cv.convert(out, start=0, end=None)
        cv.close()
    except ImportError:
        raise RuntimeError("pdf2docx not installed. Run: pip install pdf2docx")

def txt_to_pdf(inp: str, out: str) -> None:
    """Convert TXT to PDF using ReportLab."""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
    except ImportError:
        raise RuntimeError("reportlab not installed. Run: pip install reportlab")
    
    c = canvas.Canvas(out, pagesize=A4)
    width, height = A4
    x_margin, y_margin = 40, 40
    y = height - y_margin
    line_height = 14
    
    try:
        with open(inp, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.rstrip()
                if len(line) > 100:
                    words = line.split()
                    current_line = ""
                    for word in words:
                        if len(current_line) + len(word) + 1 < 100:
                            current_line += " " + word if current_line else word
                        else:
                            c.drawString(x_margin, y, current_line)
                            y -= line_height
                            if y < y_margin:
                                c.showPage()
                                y = height - y_margin
                            current_line = word
                    if current_line:
                        c.drawString(x_margin, y, current_line)
                        y -= line_height
                else:
                    c.drawString(x_margin, y, line)
                    y -= line_height
                
                if y < y_margin:
                    c.showPage()
                    y = height - y_margin
    except Exception as e:
        c.save()
        raise RuntimeError(f"Text conversion failed: {e}")
    
    c.save()

def md_to_pdf(inp: str, out: str) -> None:
    """Convert Markdown to PDF using Pandoc."""
    pandoc = which("pandoc")
    if not pandoc:
        raise RuntimeError("Pandoc not found. Install from https://pandoc.org")
    
    result = subprocess.run(
        [pandoc, inp, "-o", out, "--pdf-engine=xelatex"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        result = subprocess.run(
            [pandoc, inp, "-o", out],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            raise RuntimeError(f"Pandoc failed: {result.stderr}")
#image#

def image_to_pdf(inp: str, out: str) -> None:
    """Convert image to PDF."""
    try:
        from PIL import Image
        im = Image.open(inp)
        if im.mode in ("RGBA", "P"):
            im = im.convert("RGB")
        im.save(out, "PDF", resolution=100.0)
    except ImportError:
        raise RuntimeError("Pillow not installed. Run: pip install Pillow")

def image_convert(inp: str, out: str) -> None:
    """Convert between image formats."""
    try:
        from PIL import Image
        im = Image.open(inp)
        
        if out.lower().endswith(('.jpg', '.jpeg')):
            if im.mode in ("RGBA", "P"):
                background = Image.new("RGB", im.size, (255, 255, 255))
                if im.mode == "P":
                    im = im.convert("RGBA")
                background.paste(im, mask=im.split()[-1] if im.mode == "RGBA" else None)
                im = background
        
        im.save(out)
    except ImportError:
        raise RuntimeError("Pillow not installed. Run: pip install Pillow")

def pdf_to_images(inp: str, out_pattern: str) -> None:
    """Convert PDF to images."""
    try:
        from pdf2image import convert_from_path
        from pdf2image.exceptions import PDFInfoNotInstalledError
    except ImportError:
        raise RuntimeError("pdf2image not installed. Run: pip install pdf2image")
    kwargs = {}
    if IS_WINDOWS:
        poppler_paths = [
            r"C:\Program Files\poppler\bin",
            r"C:\poppler\bin",
            r"C:\Users\{}\poppler\bin".format(os.environ.get('USERNAME')),
        ]
        for path in poppler_paths:
            if os.path.exists(path):
                kwargs['poppler_path'] = path
                break
    
    try:
        pages = convert_from_path(inp, dpi=200, **kwargs)
    except PDFInfoNotInstalledError:
        if IS_WINDOWS:
            raise RuntimeError("Poppler not found. Install: choco install poppler")
        else:
            raise RuntimeError("poppler not installed. Install: sudo apt install poppler-utils")
    except Exception as e:
        raise RuntimeError(f"PDF conversion failed: {e}")
    
    fmt = Path(out_pattern).suffix[1:].lower() or "png"
    base = out_pattern.replace(f"{{page}}.{fmt}", "").replace(f".{fmt}", "")
    
    for i, page in enumerate(pages, 1):
        out_path = f"{base}_{i:03d}.{fmt}" if "{page}" in out_pattern else out_pattern.format(page=i)
        page.save(out_path, fmt.upper() if fmt != "jpg" else "JPEG")

#pdf section

def merge_pdfs(inputs: List[str], out: str) -> None:
    """Merge multiple PDFs into one."""
    try:
        from pypdf import PdfMerger
    except ImportError:
        try:
            from PyPDF2 import PdfMerger
        except ImportError:
            raise RuntimeError("pypdf not installed. Run: pip install pypdf")
    
    if len(inputs) < 2:
        raise ValueError("Need at least 2 files to merge")
    
    merger = PdfMerger()
    try:
        for f in inputs:
            if not os.path.exists(f):
                raise FileNotFoundError(f"File not found: {f}")
            merger.append(f)
        merger.write(out)
    finally:
        merger.close()

def split_pdf(inp: str, outdir: str) -> None:
    """Split PDF into individual pages."""
    try:
        from pypdf import PdfReader, PdfWriter
    except ImportError:
        try:
            from PyPDF2 import PdfReader, PdfWriter
        except ImportError:
            raise RuntimeError("pypdf not installed. Run: pip install pypdf")
    
    if not os.path.exists(inp):
        raise FileNotFoundError(f"File not found: {inp}")
    
    ensure_dir(outdir)
    reader = PdfReader(inp)
    
    for i, page in enumerate(reader.pages):
        writer = PdfWriter()
        writer.add_page(page)
        out_path = os.path.join(outdir, f"page_{i+1:03d}.pdf")
        with open(out_path, "wb") as f:
            writer.write(f)
    
    print(f"✅ Split into {len(reader.pages)} pages in {outdir}")

def compress_pdf(inp: str, out: str) -> None:
    """Compress PDF file size."""
    try:
        from pypdf import PdfReader, PdfWriter
    except ImportError:
        try:
            from PyPDF2 import PdfReader, PdfWriter
        except ImportError:
            raise RuntimeError("pypdf not installed. Run: pip install pypdf")
    
    if not os.path.exists(inp):
        raise FileNotFoundError(f"File not found: {inp}")
    
    reader = PdfReader(inp)
    writer = PdfWriter()
    
    for page in reader.pages:
        page.compress_content_streams()
        writer.add_page(page)
    
    with open(out, "wb") as f:
        writer.write(f)

def rotate_pdf(inp: str, out: str, deg: int) -> None:
    """Rotate PDF pages."""
    try:
        from pypdf import PdfReader, PdfWriter
    except ImportError:
        try:
            from PyPDF2 import PdfReader, PdfWriter
        except ImportError:
            raise RuntimeError("pypdf not installed. Run: pip install pypdf")
    
    if not os.path.exists(inp):
        raise FileNotFoundError(f"File not found: {inp}")
    
    deg = ((deg % 360) // 90) * 90
    if deg < 0:
        deg += 360
    
    reader = PdfReader(inp)
    writer = PdfWriter()
    
    for page in reader.pages:
        page.rotate(deg)
        writer.add_page(page)
    
    with open(out, "wb") as f:
        writer.write(f)

def watermark_pdf(inp: str, out: str, text: str) -> None:
    """Add text watermark to PDF."""
    try:
        from pypdf import PdfReader, PdfWriter
    except ImportError:
        try:
            from PyPDF2 import PdfReader, PdfWriter
        except ImportError:
            raise RuntimeError("pypdf not installed. Run: pip install pypdf")
    
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
    except ImportError:
        raise RuntimeError("reportlab not installed. Run: pip install reportlab")
    
    if not os.path.exists(inp):
        raise FileNotFoundError(f"File not found: {inp}")
    
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=A4)
    c.setFont("Helvetica", 60)
    c.setFillColorRGB(0.5, 0.5, 0.5, alpha=0.3)
    c.saveState()
    c.translate(300, 400)
    c.rotate(45)
    c.drawCentredString(0, 0, text)
    c.restoreState()
    c.save()
    packet.seek(0)
    
    watermark = PdfReader(packet)
    reader = PdfReader(inp)
    writer = PdfWriter()
    
    for page in reader.pages:
        page.merge_page(watermark.pages[0])
        writer.add_page(page)
    
    with open(out, "wb") as f:
        writer.write(f)

# media 

def media_convert(inp: str, out: str) -> None:
    """Convert media files using FFmpeg."""
    ffmpeg = which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("FFmpeg not found. Install from https://ffmpeg.org")
    
    if not os.path.exists(inp):
        raise FileNotFoundError(f"File not found: {inp}")
    
    result = subprocess.run(
        [ffmpeg, "-y", "-i", inp, out],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True
    )
    
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg failed: {result.stderr}")

CONVERTERS = {
    ("pdf", "docx"): convert_pdf_to_docx,
    ("docx", "pdf"): convert_docx_to_pdf,
    ("doc", "pdf"): convert_doc_to_pdf,
    ("txt", "pdf"): txt_to_pdf,
    ("md", "pdf"): md_to_pdf,
    ("png", "pdf"): image_to_pdf,
    ("jpg", "pdf"): image_to_pdf,
    ("jpeg", "pdf"): image_to_pdf,
    ("bmp", "pdf"): image_to_pdf,
    ("webp", "pdf"): image_to_pdf,
    ("pdf", "png"): lambda i, o: pdf_to_images(i, o.replace(".png", "_{page:03d}.png")),
    ("pdf", "jpg"): lambda i, o: pdf_to_images(i, o.replace(".jpg", "_{page:03d}.jpg")),
    ("pdf", "jpeg"): lambda i, o: pdf_to_images(i, o.replace(".jpeg", "_{page:03d}.jpeg")),
    ("png", "jpg"): image_convert,
    ("png", "jpeg"): image_convert,
    ("jpg", "png"): image_convert,
    ("jpeg", "png"): image_convert,
    ("bmp", "png"): image_convert,
    ("webp", "png"): image_convert,
    ("mp4", "mp3"): media_convert,
    ("wav", "mp3"): media_convert,
    ("mp4", "wav"): media_convert,
}

def find_chain(src: str, dst: str) -> Optional[List[Tuple[str, str]]]:
    """Find 2-step conversion chain."""
    intermediates = ["pdf", "png", "jpg"]
    for mid in intermediates:
        src_mid = (src, mid) in CONVERTERS or (src == "jpeg" and mid == "jpg")
        mid_dst = (mid, dst) in CONVERTERS or (mid == "jpg" and dst == "jpeg")
        if src_mid and mid_dst:
            actual_src = "jpg" if src == "jpeg" else src
            actual_mid = "jpg" if mid == "jpeg" else mid
            actual_dst = "jpg" if dst == "jpeg" else dst
            return [(actual_src, actual_mid), (actual_mid, actual_dst)]
    return None

def dispatch(src: str, dst: str, inp: str, out: str) -> None:
    """Route conversion to appropriate handler."""
    src = src.lower().lstrip(".")
    dst = dst.lower().lstrip(".")
    
    if src == "jpeg":
        src = "jpg"
    if dst == "jpeg":
        dst = "jpg"
    
    key = (src, dst)
    
    if key in CONVERTERS:
        handler = CONVERTERS[key]
        handler(inp, out)
        return
    
    raise ValueError(f"No handler for {src} -> {dst}")

def convert_file(inp: str, out: str) -> bool:
    """Convert single file with error handling."""
    src = Path(inp).suffix[1:].lower()
    dst = Path(out).suffix[1:].lower()
    
    src_norm = "jpg" if src == "jpeg" else src
    dst_norm = "jpg" if dst == "jpeg" else dst
    
    try:
        if (src_norm, dst_norm) in CONVERTERS:
            dispatch(src, dst, inp, out)
        else:
            chain = find_chain(src_norm, dst_norm)
            if chain:
                temp_files = []
                try:
                    current_input = inp
                    for i, (from_fmt, to_fmt) in enumerate(chain):
                        if i == len(chain) - 1:
                            current_output = out
                        else:
                            temp = Path(inp).with_suffix(f".tmp_{i}.{to_fmt}")
                            temp_files.append(str(temp))
                            current_output = str(temp)
                        
                        dispatch(from_fmt, to_fmt, current_input, current_output)
                        current_input = current_output
                    
                    for temp in temp_files:
                        safe_remove(temp)
                except Exception:
                    for temp in temp_files:
                        safe_remove(temp)
                    raise
            else:
                raise ValueError(f"Unsupported conversion: {src} -> {dst}")
        
        return True
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

#menu

def menu_document_conversions():
    """Document conversion submenu."""
    while True:
        print_header()
        print("📄 DOCUMENT CONVERSIONS\n")
        print("  [1] DOCX → PDF")
        print("  [2] PDF → DOCX")
        print("  [3] DOC → PDF")
        print("  [4] TXT → PDF")
        print("  [5] MD → PDF")
        print("  [0] Back to Main Menu")
        print()
        
        choice = input("Select option: ").strip()
        
        if choice == "0":
            return
        elif choice == "1":
            inp = get_input_file("Enter DOCX file path")
            out = get_output_path(inp, "pdf")
            if confirm_overwrite(out):
                print(f"\n⏳ Converting {Path(inp).name} → PDF...")
                if convert_file(inp, out):
                    print(f"✅ Saved: {out}")
                input("\nPress Enter to continue...")
        elif choice == "2":
            inp = get_input_file("Enter PDF file path")
            out = get_output_path(inp, "docx")
            if confirm_overwrite(out):
                print(f"\n⏳ Converting {Path(inp).name} → DOCX...")
                if convert_file(inp, out):
                    print(f"✅ Saved: {out}")
                input("\nPress Enter to continue...")
        elif choice == "3":
            inp = get_input_file("Enter DOC file path")
            out = get_output_path(inp, "pdf")
            if confirm_overwrite(out):
                print(f"\n⏳ Converting {Path(inp).name} → PDF...")
                if convert_file(inp, out):
                    print(f"✅ Saved: {out}")
                input("\nPress Enter to continue...")
        elif choice == "4":
            inp = get_input_file("Enter TXT file path")
            out = get_output_path(inp, "pdf")
            if confirm_overwrite(out):
                print(f"\n⏳ Converting {Path(inp).name} → PDF...")
                if convert_file(inp, out):
                    print(f"✅ Saved: {out}")
                input("\nPress Enter to continue...")
        elif choice == "5":
            inp = get_input_file("Enter MD file path")
            out = get_output_path(inp, "pdf")
            if confirm_overwrite(out):
                print(f"\n⏳ Converting {Path(inp).name} → PDF...")
                if convert_file(inp, out):
                    print(f"✅ Saved: {out}")
                input("\nPress Enter to continue...")

def menu_image_conversions():
    """Image conversion submenu."""
    formats = [("PNG", "png"), ("JPG", "jpg"), ("BMP", "bmp"), ("WEBP", "webp"), ("PDF", "pdf")]
    
    while True:
        print_header()
        print("🖼️  IMAGE CONVERSIONS\n")
        print("  Convert FROM any format TO any format\n")
        print("  Supported: PNG, JPG, BMP, WEBP, PDF\n")
        print("  [1] Select input file and convert")
        print("  [0] Back to Main Menu")
        print()
        
        choice = input("Select option: ").strip()
        
        if choice == "0":
            return
        elif choice == "1":
            inp = get_input_file("Enter image file path")
            src_ext = Path(inp).suffix[1:].upper()
            print(f"\nDetected format: {src_ext}")
            print("Available output formats:")
            for i, (name, ext) in enumerate(formats, 1):
                marker = "→" if ext.upper() == src_ext else " "
                print(f"  [{i}] {marker} {name}")
            
            fmt_choice = input("\nSelect output format (number): ").strip()
            try:
                idx = int(fmt_choice) - 1
                if 0 <= idx < len(formats):
                    out_ext = formats[idx][1]
                    out = get_output_path(inp, out_ext)
                    if confirm_overwrite(out):
                        print(f"\n⏳ Converting {Path(inp).name} → {out_ext.upper()}...")
                        if convert_file(inp, out):
                            print(f"✅ Saved: {out}")
                        input("\nPress Enter to continue...")
            except ValueError:
                print("❌ Invalid selection")
                input("\nPress Enter to continue...")
def install_dependencies():
    """Auto-install all required dependencies."""
    print_header()
    print("🔧 DEPENDENCY INSTALLER\n")
    
    import subprocess
    import sys
    
    # Python packages to install
    packages = [
        "Pillow",
        "pypdf",
        "pdf2image",
        "pdf2docx",
        "reportlab",
        "tqdm",
    ]
    
    # Platform-specific packages
    if IS_WINDOWS:
        packages.extend(["docx2pdf", "pywin32"])
    
    print("📦 Installing Python packages...")
    print("-" * 40)
    
    for pkg in packages:
        print(f"\n⏳ Installing {pkg}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
            print(f"✅ {pkg} installed")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {pkg}: {e}")
    
    print("\n" + "=" * 40)
    print("🖥️  SYSTEM DEPENDENCIES")
    print("=" * 40)
    
    if IS_WINDOWS:
        print("""
⚠️  Please install these manually:

1. FFmpeg:
   - Download from: https://ffmpeg.org/download.html#build-windows
   - Or use: winget install ffmpeg
   - Or: choco install ffmpeg

2. LibreOffice (for DOCX/DOC conversion):
   - Download from: https://www.libreoffice.org/download/download/

3. Pandoc (for Markdown conversion):
   - Download from: https://pandoc.org/installing.html
   - Or: winget install pandoc

4. Poppler (for PDF to Image):
   - Download from: https://github.com/oschwartz10612/poppler-windows/releases/
   - Or: choco install poppler
""")
    else:
        print("""
📋 Run these commands to install system dependencies:

# Ubuntu/Debian:
sudo apt update
sudo apt install -y ffmpeg libreoffice pandoc poppler-utils

# Fedora:
sudo dnf install -y ffmpeg libreoffice pandoc poppler-utils

# Arch:
sudo pacman -S ffmpeg libreoffice pandoc poppler

# macOS:
brew install ffmpeg libreoffice pandoc poppler
""")
    
    input("\nPress Enter to continue...")

def menu_pdf_operations():
    """PDF operations submenu."""
    while True:
        print_header()
        print("📑 PDF OPERATIONS\n")
        print("  [1] Merge PDFs")
        print("  [2] Split PDF")
        print("  [3] Compress PDF")
        print("  [4] Rotate PDF")
        print("  [5] Add Watermark")
        print("  [6] PDF → Images (PNG/JPG)")
        print("  [0] Back to Main Menu")
        print()
        
        choice = input("Select option: ").strip()
        
        if choice == "0":
            return
        elif choice == "1":
            files = []
            print("Enter PDF files to merge (empty line to finish):")
            while True:
                f = input(f"  File {len(files)+1}: ").strip().strip('"')
                if not f:
                    break
                if os.path.exists(f):
                    files.append(f)
                else:
                    print(f"  ❌ File not found: {f}")
            
            if len(files) < 2:
                print("❌ Need at least 2 files to merge")
                input("\nPress Enter to continue...")
                continue
            
            out = input("Output file name (e.g., merged.pdf): ").strip()
            if not out.endswith('.pdf'):
                out += '.pdf'
            if confirm_overwrite(out):
                print(f"\n⏳ Merging {len(files)} PDFs...")
                try:
                    merge_pdfs(files, out)
                    print(f"✅ Saved: {out}")
                except Exception as e:
                    print(f"❌ Error: {e}")
                input("\nPress Enter to continue...")
        
        elif choice == "2":
            inp = get_input_file("Enter PDF file path")
            outdir = input("Output directory (default: pages): ").strip() or "pages"
            print(f"\n⏳ Splitting PDF...")
            try:
                split_pdf(inp, outdir)
            except Exception as e:
                print(f"❌ Error: {e}")
            input("\nPress Enter to continue...")
        
        elif choice == "3":
            inp = get_input_file("Enter PDF file path")
            out = get_output_path(inp, "_compressed.pdf")
            if confirm_overwrite(out):
                print(f"\n⏳ Compressing PDF...")
                try:
                    compress_pdf(inp, out)
                    print(f"✅ Saved: {out}")
                except Exception as e:
                    print(f"❌ Error: {e}")
                input("\nPress Enter to continue...")
        
        elif choice == "4":
            inp = get_input_file("Enter PDF file path")
            deg = input("Rotation degrees (90, 180, 270, -90): ").strip()
            try:
                deg = int(deg)
                out = get_output_path(inp, f"_rotated{deg}.pdf")
                if confirm_overwrite(out):
                    print(f"\n⏳ Rotating PDF {deg}°...")
                    try:
                        rotate_pdf(inp, out, deg)
                        print(f"✅ Saved: {out}")
                    except Exception as e:
                        print(f"❌ Error: {e}")
                input("\nPress Enter to continue...")
            except ValueError:
                print("❌ Invalid rotation value")
                input("\nPress Enter to continue...")
        
        elif choice == "5":
            inp = get_input_file("Enter PDF file path")
            text = input("Watermark text: ").strip()
            if text:
                out = get_output_path(inp, "_watermarked.pdf")
                if confirm_overwrite(out):
                    print(f"\n⏳ Adding watermark...")
                    try:
                        watermark_pdf(inp, out, text)
                        print(f"✅ Saved: {out}")
                    except Exception as e:
                        print(f"❌ Error: {e}")
                input("\nPress Enter to continue...")
        
        elif choice == "6":
            inp = get_input_file("Enter PDF file path")
            fmt = input("Output format (png/jpg): ").strip().lower() or "png"
            if fmt not in ('png', 'jpg'):
                fmt = 'png'
            out = get_output_path(inp, f".{fmt}")
            print(f"\n⏳ Converting PDF to {fmt.upper()} images...")
            try:
                pdf_to_images(inp, out.replace(f".{fmt}", "_{page:03d}.{fmt}"))
                print(f"✅ Images saved")
            except Exception as e:
                print(f"❌ Error: {e}")
            input("\nPress Enter to continue...")

def menu_media_conversions():
    """Media conversion submenu."""
    while True:
        print_header()
        print("🎵 MEDIA CONVERSIONS\n")
        print("  [1] MP4 → MP3 (Extract audio)")
        print("  [2] WAV → MP3")
        print("  [3] MP4 → WAV")
        print("  [0] Back to Main Menu")
        print()
        
        choice = input("Select option: ").strip()
        
        if choice == "0":
            return
        elif choice in ("1", "2", "3"):
            inp = get_input_file("Enter media file path")
            if choice == "1":
                out = get_output_path(inp, "mp3")
            elif choice == "2":
                out = get_output_path(inp, "mp3")
            else:
                out = get_output_path(inp, "wav")
            
            if confirm_overwrite(out):
                print(f"\n⏳ Converting {Path(inp).name}...")
                if convert_file(inp, out):
                    print(f"✅ Saved: {out}")
                input("\nPress Enter to continue...")

def menu_custom_conversion():
    """Custom conversion - any to any."""
    print_header()
    print("🔄 CUSTOM CONVERSION\n")
    print("Convert any supported format to any other format\n")
    
    inp = get_input_file("Enter input file path")
    src_ext = Path(inp).suffix[1:].upper()
    print(f"\nDetected input format: {src_ext}")
    
    print("\nSupported output formats:")
    all_formats = ["PDF", "DOCX", "PNG", "JPG", "BMP", "WEBP", "MP3", "WAV"]
    for i, fmt in enumerate(all_formats, 1):
        print(f"  [{i}] {fmt}")
    
    choice = input("\nSelect output format (number or name): ").strip().upper()
    
    out_ext = None
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(all_formats):
            out_ext = all_formats[idx].lower()
    else:
        out_ext = choice.lower().lstrip('.')
    
    if out_ext:
        out = get_output_path(inp, out_ext)
        if confirm_overwrite(out):
            print(f"\n⏳ Converting {Path(inp).name} → {out_ext.upper()}...")
            if convert_file(inp, out):
                print(f"✅ Saved: {out}")
        input("\nPress Enter to continue...")
    else:
        print("❌ Invalid format selected")
        input("\nPress Enter to continue...")

def main_menu():
    """Main interactive menu."""
    while True:
        print_header()
        print("🎯 MAIN MENU\n")
        print("  [1] 📄 Document Conversions")
        print("  [2] 🖼️  Image Conversions")
        print("  [3] 📑 PDF Operations")
        print("  [4] 🎵 Media Conversions")
        print("  [5] 🔄 Custom Conversion (Any → Any)")
        print("  [6] 🔍 System Check (Doctor)")
        print("  [7] 🔧 Install Dependencies")  # NEW OPTION
        print("  [0] ❌ Exit")
        print()
        
        choice = input("Select option: ").strip()
        
        if choice == "0":
            print_header()
            print("👋 Goodbye! Thanks for using Convctl.\n")
            sys.exit(0)
        elif choice == "1":
            menu_document_conversions()
        elif choice == "2":
            menu_image_conversions()
        elif choice == "3":
            menu_pdf_operations()
        elif choice == "4":
            menu_media_conversions()
        elif choice == "5":
            menu_custom_conversion()
        elif choice == "6":
            doctor()
        elif choice == "7":  # NEW
            install_dependencies()
        else:
            print("❌ Invalid option")
            time.sleep(1)
#cli

def cli_mode():
    """Original CLI mode for scripting."""
    parser = argparse.ArgumentParser(
        description="Universal File Converter",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s input.docx output.pdf
  %(prog)s --merge a.pdf b.pdf out.pdf
  %(prog)s input.pdf pages/ --split
        """
    )
    
    parser.add_argument("input", nargs="?", help="Input file")
    parser.add_argument("output", nargs="?", help="Output file")
    parser.add_argument("--merge", action="store_true")
    parser.add_argument("--split", action="store_true")
    parser.add_argument("--compress", action="store_true")
    parser.add_argument("--rotate", type=int)
    parser.add_argument("--watermark")
    parser.add_argument("--batch", action="store_true")
    parser.add_argument("--doctor", action="store_true")
    parser.add_argument("--cli", action="store_true", help="Force CLI mode")
    
    args = parser.parse_args()
    
    if args.doctor:
        doctor()
        return
    
    if args.merge:
        inputs = sys.argv[2:-1]
        output = sys.argv[-1]
        merge_pdfs(inputs, output)
        print(f"Merged {len(inputs)} files into {output}")
        return
    
    if args.split:
        split_pdf(args.input, args.output or "pages")
        return
    
    if args.compress:
        compress_pdf(args.input, args.output)
        return
    
    if args.rotate:
        rotate_pdf(args.input, args.output, args.rotate)
        return
    
    if args.watermark:
        watermark_pdf(args.input, args.output, args.watermark)
        return
    
    if not args.input or not args.output:
        parser.print_help()
        return
    
    if convert_file(args.input, args.output):
        print("Done.")
    else:
        sys.exit(1)

def main():
    """Entry point - auto-detect interactive or CLI mode."""
    if len(sys.argv) > 1 and sys.argv[1] not in ('--cli',):
        cli_mode()
    else:
        try:
            main_menu()
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!")
            sys.exit(0)

if __name__ == "__main__":
    main()