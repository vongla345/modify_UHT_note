import io
import os
import fitz
import datetime
import streamlit as st
from streamlit_pdf_viewer import pdf_viewer

from utils import insert_patch_all_pages, create_text, get_date

DATE_MILTSTONE = datetime.date(2025,7,1)

setting = {
    'type': None,
    'patch_path': None,
    'pixel_coords': None,
    'pixel_coords_adress': None,
    'date': None,
    'metadata': None,
    'file_date': None,
}
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
        setting['type'] = 'thu_tien'
        setting['patch_path'] = "template/kho_hiep_phuoc_delivery_note_1.png"
        setting['pixel_coords'] = (1330, 1670, 1370, 1440)
        setting['file_date'] = get_date(pdf_bytes, 'thu_tien')
        setting['pixel_coords_adress'] = (860, 2500, 310, 370)
        
        if st.checkbox("Chỉnh sửa ngày"):
            setting['date'] = st.date_input("Nhập ngày giao hàng cần sửa", format='DD-MM-YYYY')
            setting['metadata'] = {
                'day':{
                    'value': f"{setting['date'].day:02d}",
                    'pixel_records':  (620, 680, 940, 999),
                    'font_size': 15,
                    'is_year': False
                },
                'month': {
                    'value': f"{setting['date'].month:02d}",
                    'pixel_records': (953, 1013, 940, 999),
                    'font_size': 15,
                    'is_year': False
                },
                'year': {
                    'value': str(setting['date'].year),
                    'pixel_records': (1225, 1375, 940, 999),
                    'font_size': 14,
                    'is_year': True
                }
            }
            
    elif raido_button == "Phiếu xuất kho":
        setting['type'] = 'xuat_kho'
        setting['patch_path'] = "template/kho_hiep_phuoc_material_document.png"
        setting['pixel_coords'] = (3570, 4100, 1030, 1100)
        setting['pixel_coords_adress'] = (920, 3000, 360, 430)
        setting['file_date'] = get_date(pdf_bytes, 'xuat_kho')
        

            
    
    if st.button("Process"):
    
        doc = insert_patch_all_pages(doc, setting['patch_path'], setting['pixel_coords'])
    
        if setting['type'] == 'thu_tien' and setting['date']:
            font_path = "times.ttf"  # Đường dẫn đến font của bạn

            for key, value in setting['metadata'].items():
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
            
            
            if setting['date'] < DATE_MILTSTONE:
                doc = insert_patch_all_pages(
                    doc=doc,
                    patch_path='template/old_adress_thu_tien.png',
                    pixel_coords=setting['pixel_coords_adress'],
                    dpi=300,
                )
        elif setting['type'] == 'xuat_kho' and setting['file_date'] and setting['file_date'] < DATE_MILTSTONE:
            doc = insert_patch_all_pages(
                doc=doc,
                patch_path='template/old_adress_xuat_kho.png',
                pixel_coords=setting['pixel_coords_adress'],
                dpi=300,
            )
        
        output = io.BytesIO()
        doc.save(output)
        doc.close()
        pdf_bytes_output = output.getvalue()
        
        pdf_viewer(
            pdf_bytes_output, 
            height = 800,
            zoom_level=1.0,      
            viewer_align="center",         
            show_page_separator=False 
        )
        
        st.download_button(
            label="Download PDF",
            data=pdf_bytes_output,
            file_name=output_path,
            mime="application/pdf"
        )

# Example: Process only specific pages (e.g., pages 1, 2, and 3)
# insert_patch_all_pages(pdf_path, "01.07_selected_pages.pdf", patch_path, pixel_coords, pages=[0, 1, 2])