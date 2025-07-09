import streamlit as st
import fitz  # PyMuPDF
import io

st.title("Change Outbound Warehouse")


def insert_patch_all_pages(pdf_bytes, output_path, patch_path, pixel_coords, dpi=300, pages=None):
    """
    Insert an image patch into all pages (or specified pages) of a PDF.
    
    Args:
        pdf_bytes: PDF file as bytes
        output_path: Output PDF file path
        patch_path: Image patch file path
        pixel_coords: Tuple of (x0, x1, top, bottom) in pixel coordinates
        dpi: DPI used when extracting the image (default 300)
        pages: List of page numbers to process (0-based). If None, process all pages.
    """
    # Unpack and convert coordinates
    x0_px, x1_px, top_px, bottom_px = pixel_coords
    scale_factor = 72.0 / dpi
    
    x0_pt = x0_px * scale_factor
    x1_pt = x1_px * scale_factor
    top_pt = top_px * scale_factor
    bottom_pt = bottom_px * scale_factor
    
    rect = fitz.Rect(x0_pt, top_pt, x1_pt, bottom_pt)
    
    # Open PDF from bytes
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    
    # Determine which pages to process
    if pages is None:
        pages_to_process = range(len(doc))
    else:
        pages_to_process = pages
    
    processed_count = 0
    
    # Process each page
    for page_num in pages_to_process:
        if page_num < len(doc):
            page = doc[page_num]
            
            # Draw white rectangle to cover existing text
            page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))
            
            # Insert the image patch
            page.insert_image(rect, filename=patch_path)
            
            processed_count += 1
    
    # Return the modified document
    return doc


raido_button = st.radio("Select patch", ["Phiếu giao hàng thu tiền", 
                                        "Phiếu xuất kho"])

if raido_button == "Phiếu giao hàng thu tiền":
    patch_path = "kho_hiep_phuoc_delivery_note.png"
    pixel_coords = (1330, 1670, 1370, 1440)
elif raido_button == "Phiếu xuất kho":
    patch_path = "kho_hiep_phuoc_material_document.png"
    pixel_coords = (3570, 4100, 1030, 1100)

uploaded_file = st.file_uploader("Tải file pdf", type=["pdf"])

if uploaded_file:
    # Read the uploaded file into bytes
    pdf_bytes = uploaded_file.read()
    output_path = f"{uploaded_file.name}_updated.pdf"

    doc = insert_patch_all_pages(pdf_bytes, output_path, patch_path, pixel_coords)
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