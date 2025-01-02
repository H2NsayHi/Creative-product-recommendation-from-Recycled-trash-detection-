import streamlit as st
from PIL import Image
import numpy as np
from model import GetTopSimilar
from getData import GetMatrixCompare, GetInputArray
import os
import time
from io import BytesIO

# Function for image processing and recycling recommendations
def imgProcessing(image):
    # Get input array using GetInputArray
    num_of_ingredient = 24  # Assuming number of ingredients
    input_array = GetInputArray(image, num_of_ingredient).numpy_input_array

    # Assuming your JSON file path
    json_file_path = 'data.json'

    # Get compare matrix using GetMatrixCompare
    gmc = GetMatrixCompare(json_file_path)
    compare_matrix = gmc.matrix
    materials = {material["id"]: material["name"] for material in gmc.materials}
    recycled_items = {item["id"]: item for item in gmc.recycled}

    # Display identified materials
    st.write("Identified Materials")
    for material_id, material_quantity in enumerate(input_array):
        if material_quantity != 0:
            material_name = materials.get(material_id + 1, "Unknown Material")
            st.write(f"- You have {material_quantity} {material_name}")

    for i in range(len(materials)):
        col1, col2 = st.sidebar.columns(2)
        col1.write(f"ID: {i+1}")
        col2.write(f"{materials.get(i + 1, 'Unknown Material')}")

    adjust = st.text_input("Confirm the quantities.")
    st.write(" Type 'ok' to confirm. Or adjust specific value use ~ EX: 1:3, 2:4")
    if adjust:
        if adjust == "ok":
            pass
        else:
            pairs = adjust.split(", ")
            for pair in pairs:
                index, value = pair.split(":")
                index = int(index)
                value = int(value)
                input_array[index - 1] = value

        for material_id, material_quantity in enumerate(input_array):
            if material_quantity != 0:
                material_name = materials.get(material_id + 1, "Unknown Material")
                st.write(f"- You have {material_quantity} {material_name}")

        # Get top similar using GetTopSimilar
        top_similar = GetTopSimilar(input_array, compare_matrix)

        # Display top similar recycled items
        for recycled_id, euclidean_distance in zip(top_similar.recycled_id, top_similar.euclidean_distances):
            if recycled_id == 15 or recycled_id == 16:
                continue

            col1, col2 = st.columns(2)
            with col1:
                recycled_image_path = f'recycled_images/{recycled_id+1}.png'
                if os.path.exists(recycled_image_path):
                    recycled_image = Image.open(recycled_image_path)
                    st.image(recycled_image, caption=f'Recycled ID: {recycled_id+1}', use_container_width=True)
                else:
                    st.write(f'Image not found for Recycled ID: {recycled_id+1}')
            with col2:
                recycled_item = recycled_items[recycled_id+1]
                st.write(f'Recycled ID: {recycled_id+1}')
                st.write(f'Error rate: {euclidean_distance}')
                st.write(f"Name: {recycled_item['name']}")
                st.write(f"URL: {recycled_item['url']}")
                st.write(f"Difficulty Level: {recycled_item['difficult_level']}")
                st.write(f"Danger Level: {recycled_item['danger_level']}")
                compare_materials = input_array - compare_matrix[recycled_id]
                for i, _ in enumerate(compare_materials):
                    if _ == 0:
                        pass
                    elif _ > 0:
                        st.write(f"You are redundant  {int(_)} material: {materials.get(i+1)}")
                    else:
                        st.write(f"You are missing {int(-_)} material: {materials.get(i+1)}")
                st.write('--------------------------------')

# Initialize session state
if 'screen' not in st.session_state:
    st.session_state.screen = 'welcome'  # Default screen
if 'selected_class' not in st.session_state:
    st.session_state.selected_class = None  # Track selected class

# Welcome screen
if st.session_state.screen == 'welcome':
    # Add a title and subtitle
    st.markdown("<h1 style='text-align: center;'>Đăng nhập</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Bạn là ai?</h3>", unsafe_allow_html=True)
    
    # Add some spacing
    st.write("")
    st.write("")
    
    # Create columns for buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button('Học sinh', key='hoc_sinh'):
            st.session_state.screen = 'student'
            st.rerun()
    
    with col2:
        if st.button('Giáo viên', key='giao_vien'):
            st.session_state.screen = 'teacher'
            st.rerun()
    
    with col3:
        if st.button('Phụ Huynh', key='phu_huynh'):
            st.write("Phụ Huynh option is currently under development.")  # Placeholder for Phụ Huynh
    
    # Add some spacing
    st.write("")
    st.write("")
    
    # Add a divider for visual separation
    st.markdown("---")
    
    # Add a footer or additional information
    st.markdown("<p style='text-align: center;'>Chào mừng bạn đến với Lớp học thông minh</p>", unsafe_allow_html=True)

# Student screen
# Student screen
if st.session_state.screen == 'student':
    # Add a title and subtitle
    st.markdown("<h1 style='text-align: center;'>Học sinh</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Tìm kiếm sản phẩm tái chế</h3>", unsafe_allow_html=True)
    
    # Add some spacing
    st.write("")
    st.write("")
    
    # Add a radio button to select the input method
    input_method = st.radio("Chọn phương thức nhập liệu:", ("Tải ảnh lên", "Chụp ảnh"))
    
    # Add a divider for visual separation
    st.markdown("---")
    
    start = time.time()  # Start time

    if input_method == "Tải ảnh lên":
        # File uploader for image
        st.markdown("### 📤 **Tải ảnh lên**")
        image_file = st.file_uploader("Chọn một ảnh từ thiết bị của bạn", type=['jpg', 'png', 'webp'])
        if image_file is not None:
            # Display the uploaded image
            image = Image.open(image_file)
            st.image(image, caption='Ảnh đã tải lên', use_container_width=True)
            imgProcessing(image)

    elif input_method == "Chụp ảnh":
        # Camera input to take a photo
        st.markdown("### 📷 **Chụp ảnh**")
        picture = st.camera_input("Chụp ảnh từ camera của bạn")
        if picture is not None:
            # Convert the captured image to bytes
            image_bytes = picture.read()
            # Convert the bytes to a PIL Image
            image = Image.open(BytesIO(image_bytes))
            imgProcessing(image)
    
    # Add a divider for visual separation
    st.markdown("---")
    
    # Calculate time taken
    end = time.time()
    st.write(f"⏱️ **Thời gian xử lý:** {end - start:.2f} giây")
    
    # Add a footer or additional information
    st.markdown("<p style='text-align: center;'>Hãy tái chế để bảo vệ môi trường!</p>", unsafe_allow_html=True)

# Teacher screen
if st.session_state.screen == 'teacher':
    st.title('Lớp học thông minh')
    
    # Display class buttons
    if st.button('Lớp 6A1'):
        st.session_state.selected_class = 'Lớp 6A1'
        st.session_state.screen = 'class_detail'
        st.rerun()
    
    if st.button('Lớp 6A2'):
        st.session_state.selected_class = 'Lớp 6A2'
        st.session_state.screen = 'class_detail'
        st.rerun()
    
    if st.button('Lớp 7A2'):
        st.session_state.selected_class = 'Lớp 7A2'
        st.session_state.screen = 'class_detail'
        st.rerun()
    
    if st.button('Lớp 7A3'):
        st.session_state.selected_class = 'Lớp 7A3'
        st.session_state.screen = 'class_detail'
        st.rerun()

# Class detail screen
if st.session_state.screen == 'class_detail':
    st.title(f'Chi tiết lớp: {st.session_state.selected_class}')
    
    if st.session_state.selected_class == 'Lớp 6A1':
        # Highlighted section for assignments
        st.markdown("### 📅 **Ngày 12/12**")
        st.markdown("- **Hãy nghiên cứu về động cơ 2 chiều**")
        st.markdown("- **Làm 1 sản phẩm theo ứng dụng của động cơ 2 chiều**")
        
        st.markdown("### 📅 **Ngày 13/12**")
        st.markdown("- **Hãy nghiên cứu về động cơ 2 chiều**")
        st.markdown("- **Làm 1 sản phẩm theo ứng dụng của động cơ 2 chiều**")
        st.markdown("- **Làm 1 sản phẩm theo ứng dụng của động cơ 2 chiều**")
        
        # Divider line
        st.markdown("---")
        
        # Submission status with highlighted count
        st.markdown("### 📤 **Đã nộp: 30/30**")
        
        # Student list with columns for better organization
        st.markdown("### 📝 **Danh sách học sinh**")
        col1, col2, col3 = st.columns([3, 2, 2])
        with col1:
            st.markdown("**Họ và tên**")
        with col2:
            st.markdown("**Xem bài**")
        with col3:
            st.markdown("**Nhận xét**")
        
        # Student entries
        students = [
            "Nguyễn Văn A", "Nguyễn Văn B", "Nguyễn Văn C", "Nguyễn Văn D", "Nguyễn Văn E"
        ]
        for i, student in enumerate(students):  # Use index to create unique keys
            col1, col2, col3 = st.columns([3, 2, 2])
            with col1:
                st.write(student)
            with col2:
                st.button(f"Xem bài", key=f"view_{student}_{i}")  # Unique key
            with col3:
                st.button(f"Nhận xét", key=f"comment_{student}_{i}")  # Unique key
        
        # Divider line
        st.markdown("---")
        
        # Back button to return to the teacher screen
        if st.button('Quay lại'):
            st.session_state.screen = 'teacher'
            st.rerun()