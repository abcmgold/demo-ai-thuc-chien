"""Component giao diện dùng chung cho Trợ lý Du lịch Đắk Lắk."""

from html import escape
import base64
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageOps
import streamlit as st
import streamlit.components.v1 as components

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
IMAGES = ASSETS / "images"


def apply_theme() -> None:
    css = (ASSETS / "style.css").read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def page_header(tag: str, title: str, subtitle: str = "") -> None:
    st.markdown(
        f'<div class="dl-page-head"><div class="dl-eyebrow">{escape(tag)}</div>'
        f'<h1 class="dl-page-title">{escape(title)}</h1>'
        f'<p class="dl-page-subtitle">{escape(subtitle)}</p></div>',
        unsafe_allow_html=True,
    )


def image_slot(filename: str, label: str, height: int = 220) -> None:
    """Hiển thị ảnh được cung cấp nếu có, nếu chưa thì giữ khung chờ ảnh."""
    path = IMAGES / filename
    if path.is_file():
        st.image(str(path), caption=label, width="stretch")
        return
    st.markdown(
        f'<div class="dl-image-slot" style="--slot-height:{int(height)}px">'
        f'<span class="dl-image-slot-mark">ĐL</span><span>{escape(label)}</span></div>',
        unsafe_allow_html=True,
    )


def section_title(eyebrow: str, title: str, note: str = "") -> None:
    st.markdown(
        f'<div class="dl-section-title"><div class="dl-eyebrow">{escape(eyebrow)}</div>'
        f'<h2>{escape(title)}</h2><p>{escape(note)}</p></div>',
        unsafe_allow_html=True,
    )


@st.cache_data(show_spinner=False)
def _image_uri(filename: str, modified: int) -> str:
    with Image.open(IMAGES / filename) as original:
        photo = ImageOps.exif_transpose(original).convert("RGB")
        photo.thumbnail((1440, 1000))
        output = BytesIO()
        photo.save(output, format="JPEG", quality=85)
    return "data:image/jpeg;base64," + base64.b64encode(output.getvalue()).decode("ascii")


def photo_uri(filename: str) -> str:
    path = IMAGES / filename
    return _image_uri(filename, path.stat().st_mtime_ns) if path.is_file() else ""


def destination_card(name: str, category: str, description: str, image: str, image_label: str, slug: str | None = None) -> None:
    safe_name = "".join(char.lower() if char.isalnum() else "-" for char in name).strip("-")
    with st.container(border=True, key=f"destination-{safe_name}"):
        if slug and (uri := photo_uri(image)):
            st.markdown(f'<a class="dl-photo-link" href="dia-diem?destination={escape(slug, quote=True)}" target="_self" aria-label="Khám phá {escape(name, quote=True)}"><img src="{uri}" alt="{escape(image_label, quote=True)}" loading="lazy"></a>', unsafe_allow_html=True)
        else:
            image_slot(image, image_label, height=190)
        st.markdown(
            f'<div class="dl-card-category">{escape(category)}</div>'
            f'<h3 class="dl-card-title">{escape(name)}</h3>'
            f'<p class="dl-card-description">{escape(description)}</p>',
            unsafe_allow_html=True,
        )
        if slug:
            if st.button("Khám phá địa điểm →", key=f"open-{slug}", width="stretch"):
                st.session_state.selected_destination = slug
                st.switch_page("views/destination.py")


def photo_slideshow(slides: list[dict], height: int = 430) -> None:
    """Slideshow trong iframe, ảnh có sẵn ở repo, không gọi API."""
    panels, dots = [], []
    for index, slide in enumerate(slides):
        uri = photo_uri(slide["image"])
        if not uri:
            continue
        slug = slide.get("slug")
        link = f'<a href="dia-diem?destination={escape(slug, quote=True)}" target="_blank" rel="noopener">Khám phá địa điểm ↗</a>' if slug else ""
        panels.append(f'<article class="slide" aria-hidden="true"><img src="{uri}" alt="{escape(slide["subtitle"], quote=True)}"><div class="copy"><span>ĐẮK LẮK QUA ỐNG KÍNH</span><h2>{escape(slide["title"])}</h2><p>{escape(slide["subtitle"])}</p>{link}</div></article>')
        dots.append(f'<button class="dot" aria-label="Xem ảnh {len(panels)}" aria-pressed="false" data-index="{len(panels)-1}"></button>')
    if not panels:
        return
    html = """<!doctype html><html lang="vi"><head><meta charset="utf-8"><style>
    *{box-sizing:border-box}body{margin:0;font-family:Arial,sans-serif;color:#fffefa}.gallery{position:relative;height:HEIGHTpx;border-radius:20px;overflow:hidden;background:#173c32}.slide{position:absolute;inset:0;opacity:0;visibility:hidden;transition:opacity .7s ease}.slide.active{opacity:1;visibility:visible}.slide img{width:100%;height:100%;object-fit:cover}.slide::after{content:"";position:absolute;inset:0;background:linear-gradient(90deg,rgba(8,29,20,.68),rgba(8,29,20,.06)),linear-gradient(0deg,rgba(8,29,20,.7),transparent 60%)}.copy{position:absolute;left:5%;bottom:80px;right:12%;z-index:1;max-width:660px}.copy span{font-size:11px;letter-spacing:2px;color:#e5c98d}.copy h2{font-size:clamp(25px,4vw,42px);line-height:1.13;margin:15px 0}.copy p{font-size:15px;line-height:1.6;color:#f0f2e9}.copy a{display:inline-block;color:#fff;text-decoration:none;border-bottom:1px solid #e5c98d;padding:6px 0;font-size:14px}button{cursor:pointer;border:1px solid #ffffff55;background:#173c3299;color:white;backdrop-filter:blur(6px)}.arrow{position:absolute;top:45%;width:40px;height:40px;border-radius:50%;font-size:22px;z-index:2}.prev{left:15px}.next{right:15px}.controls{position:absolute;bottom:24px;left:5%;right:5%;display:flex;align-items:center;gap:12px;z-index:2}.dots{display:flex;gap:9px}.dot{height:9px;width:9px;padding:0;border-radius:50%;background:#ffffff66;border:none}.dot[aria-pressed=true]{width:27px;border-radius:8px;background:#e5c98d}.toggle{margin-left:auto;border-radius:20px;padding:8px 14px;font-size:12px}.count{font-size:12px;color:#eeeeee}button:focus-visible,a:focus-visible{outline:3px solid #e5c98d;outline-offset:4px}@media(max-width:600px){.copy{left:9%;right:9%}.copy h2{font-size:26px}.arrow{width:30px;height:30px}.prev{left:5px}.next{right:5px}}@media(prefers-reduced-motion:reduce){.slide{transition:none}}
    </style></head><body><section class="gallery" aria-label="Slideshow ảnh Đắk Lắk" aria-roledescription="carousel" tabindex="0">PANELS<button class="arrow prev" aria-label="Ảnh trước">‹</button><button class="arrow next" aria-label="Ảnh sau">›</button><div class="controls"><div class="dots">DOTS</div><span class="count"></span><button class="toggle" aria-label="Tạm dừng slideshow"></button></div></section><script>
    const root=document.querySelector('.gallery'),slides=[...document.querySelectorAll('.slide')],dots=[...document.querySelectorAll('.dot')],toggle=document.querySelector('.toggle');let current=0,timer=null,paused=matchMedia('(prefers-reduced-motion: reduce)').matches,hover=false;
    function show(index){current=(index+slides.length)%slides.length;slides.forEach((s,i)=>{s.classList.toggle('active',i===current);s.setAttribute('aria-hidden',i!==current);const a=s.querySelector('a');if(a)a.tabIndex=i===current?0:-1;});dots.forEach((d,i)=>d.setAttribute('aria-pressed',i===current));document.querySelector('.count').textContent=(current+1)+' / '+slides.length;}
    function schedule(){clearInterval(timer);toggle.textContent=paused?'▶ Phát tự động':'Ⅱ Tạm dừng';toggle.setAttribute('aria-label',paused?'Phát tự động slideshow':'Tạm dừng slideshow');if(!paused&&!hover&&!document.hidden)timer=setInterval(()=>show(current+1),5500);}
    document.querySelector('.prev').onclick=()=>{show(current-1);schedule();};document.querySelector('.next').onclick=()=>{show(current+1);schedule();};dots.forEach(d=>d.onclick=()=>{show(Number(d.dataset.index));schedule();});toggle.onclick=()=>{paused=!paused;schedule();};root.onmouseenter=()=>{hover=true;schedule();};root.onmouseleave=()=>{hover=false;schedule();};root.onfocusin=()=>{hover=true;schedule();};root.onfocusout=e=>{if(!root.contains(e.relatedTarget)){hover=false;schedule();}};root.onkeydown=e=>{if(e.key==='ArrowRight'){show(current+1);e.preventDefault();}if(e.key==='ArrowLeft'){show(current-1);e.preventDefault();}};document.addEventListener('visibilitychange',schedule);show(0);schedule();
    </script></body></html>"""
    html = html.replace("HEIGHT", str(int(height))).replace("PANELS", "".join(panels)).replace("DOTS", "".join(dots))
    components.html(html, height=height + 8, scrolling=False)


def footer() -> None:
    st.markdown(
        '<div class="dl-footer"><span>Đắk Lắk · Cao nguyên trong từng hành trình</span>'
        '<span>Trợ lý Du lịch Đắk Lắk AI</span></div>',
        unsafe_allow_html=True,
    )


def sidebar() -> None:
    st.sidebar.markdown(
        '<div class="dl-sidebar-note"><span class="dl-sidebar-note-icon">✦</span>'
        '<div><strong>Đi theo cách của bạn</strong>'
        '<p>Chọn điểm đến, nhịp đi và mức chi phù hợp.</p></div></div>',
        unsafe_allow_html=True,
    )
    st.sidebar.page_link("views/blank.py", label="Bắt đầu lên lịch trình", icon="🧭")
    st.sidebar.markdown(
        '<div class="dl-sidebar-foot">Gợi ý hành trình tôn trọng thiên nhiên và văn hóa địa phương.</div>',
        unsafe_allow_html=True,
    )
