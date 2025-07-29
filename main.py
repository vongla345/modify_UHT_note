import io
import os
import fitz
import datetime
import streamlit as st
from utils import insert_patch_all_pages, create_text

st.title("Change Ticket Information")


raido_button = st.radio("Chọn loại phiếu", ["Phiếu giao hàng thu tiền", 
                                        "Phiếu xuất kho"])

if raido_button == "Phiếu giao hàng thu tiền":
    patch_path = "kho_hiep_phuoc_delivery_note.png"
    pixel_coords = (1330, 1670, 1370, 1440)
    
    if st.checkbox("Chỉnh sửa ngày"):
        date = st.date_input("Nhập ngày giao hàng cần sửa", format='DD-MM-YYYY')
        metadata = {
            'day':{
                'value': f"{date.day:02d}",
                'pixel_records':  (620, 680, 940, 999),
                'font_size': 15,
                'is_year': False
            },
            'month': {
                'value': f"{date.month:02d}",
                'pixel_records': (953, 1013, 940, 999),
                'font_size': 15,
                'is_year': False
            },
            'year': {
                'value': str(date.year),
                'pixel_records': (1225, 1375, 940, 999),
                'font_size': 14,
                'is_year': True
            }
        }

    else:
        date = None
        
elif raido_button == "Phiếu xuất kho":
    patch_path = "kho_hiep_phuoc_material_document.png"
    pixel_coords = (3570, 4100, 1030, 1100)
    date = None

uploaded_file = st.file_uploader("Tải file pdf", type=["pdf"])

if uploaded_file:
    # Read the uploaded file into bytes
    pdf_bytes = uploaded_file.read()
    output_path = f"{uploaded_file.name}_updated.pdf"
    
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    doc = insert_patch_all_pages(doc, patch_path, pixel_coords)
    
    if date:
        font_path = "times.ttf"  # Đường dẫn đến font của bạn
        print(type(date))
        if date < datetime.date(2025, 7, 1):
            print("Change Adress")
        for key, value in metadata.items():
            output = create_text(
                text=value['value'],
                font_path=font_path,
                font_size=value['font_size'],
                is_year=value['is_year']
            )

            doc = insert_patch_all_pages(
                doc=doc,
                patch_path=output,
                pixel_coords=value['pixel_records'],
                dpi=300,
            )
            os.remove(output)

        
    pdf_bytes_output = io.BytesIO()
    doc.save(pdf_bytes_output)
    pdf_bytes_output.seek(0)
    st.download_button(
        label="Download PDF",
        data=pdf_bytes_output,
        file_name=output_path,
        mime="application/pdf"
    )

# Example: Process only specific pages (e.g., pages 1, 2, and 3)
# insert_patch_all_pages(pdf_path, "01.07_selected_pages.pdf", patch_path, pixel_coords, pages=[0, 1, 2])