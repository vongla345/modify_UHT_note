import io
import os
import fitz
import datetime
import streamlit as st
from utils import insert_patch_all_pages, create_text, get_date

DATE_MILTSTONE = datetime.date(2025,7,1)
PIXEL_COORDS_OLD_ADRESS_THU_TIEN = (860, 2500, 310, 370)
PIXEL_COORDS_OLD_ADRESS_XUAT_KHO = (920, 3000, 360, 430)
st.title("Change Ticket Information")


uploaded_file = st.file_uploader("Tải file pdf", type=["pdf"])

if uploaded_file:
    # Read the uploaded file into bytes
    pdf_bytes = uploaded_file.read()
    output_path = f"{uploaded_file.name}_updated.pdf"

    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        
    raido_button = st.radio("Chọn loại phiếu", ["Phiếu giao hàng thu tiền", 
                                            "Phiếu xuất kho"])
    
    if raido_button == "Phiếu giao hàng thu tiền":
        patch_path = "template/kho_hiep_phuoc_delivery_note_1.png"
        pixel_coords = (1330, 1670, 1370, 1440)
        file_date = get_date(pdf_bytes, 'thu_tien')

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
        patch_path = "template/kho_hiep_phuoc_material_document.png"
        pixel_coords = (3570, 4100, 1030, 1100)
        file_date = get_date(pdf_bytes, 'xuat_kho')
        
        if file_date and (file_date < DATE_MILTSTONE):
            doc = insert_patch_all_pages(
                doc=doc,
                patch_path='template/old_adress_xuat_kho.png',
                pixel_coords=PIXEL_COORDS_OLD_ADRESS_XUAT_KHO,
                dpi=300,
            )
            
        date = None
    

    doc = insert_patch_all_pages(doc, patch_path, pixel_coords)
    
    if date:
        font_path = "times.ttf"  # Đường dẫn đến font của bạn

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
        
        
        if date < DATE_MILTSTONE:
            doc = insert_patch_all_pages(
                doc=doc,
                patch_path='app/template/old_adress_thu_tien.png',
                pixel_coords=PIXEL_COORDS_OLD_ADRESS_THU_TIEN,
                dpi=300,
            )

        
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