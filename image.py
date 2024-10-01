import streamlit as st
import os
import json
from PIL import Image

selected_labels_file = 'selected_labels_file1.json'

def load_selected_labels():
    if os.path.exists(selected_labels_file):
        with open(selected_labels_file, 'r') as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
            else:
                return {}
    return {}

def save_selected_labels(selected_labels):
    with open(selected_labels_file, 'w') as f:
        json.dump(selected_labels, f, indent=4)

def add_labels(label, label_options):
    if label and label.lower() not in [l.lower() for l in label_options]:
        label_options.append(label)
        st.session_state.label_options = label_options
        st.success(f"Label '{label}' added.")
    elif label.lower() in [l.lower() for l in label_options]:
        st.warning(f"Label '{label}' already exists.")
    else:
        st.warning("Please enter a valid label.")

def remove_labels(label, label_options):
    if label and label in label_options:
        if label not in [lbl for lbl in load_selected_labels().values()]:
            label_options.remove(label)
            st.session_state.label_options = label_options
            st.success(f"Label '{label}' removed.")
        else:
            st.warning(f'There are some images that are labeled with "{label}".')
    elif not label:
        st.warning("Please select a label to remove.")
    else:
        st.warning("Label does not exist.")

def calculate_number_of_pages(directory_path, images_per_page=15):
    files = os.listdir(directory_path)
    image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
    
    if not image_files:
        st.info("No images present in this directory.")
        return 0, []

    total_pages = (len(image_files) + images_per_page - 1) // images_per_page
    return total_pages, image_files

def display_images(image_files, directory_path, page, images_per_page=15, image_size=(150, 150), selected_labels=None):
    start_index = (page - 1) * images_per_page
    end_index = min(start_index + images_per_page, len(image_files))
    current_images = image_files[start_index:end_index]

    saved_selected_labels = load_selected_labels()

    cols = st.columns(3)
    for idx, image_file in enumerate(current_images):
        with cols[idx % 3]:
            image_path = os.path.join(directory_path, image_file)
            img = Image.open(image_path)
            img = img.resize(image_size)
            st.image(img, use_column_width=True)

            current_label = saved_selected_labels.get(image_file, "")

            if selected_labels:
                selected_label = st.radio(
                    "",
                    options=selected_labels,
                    index=(selected_labels.index(current_label) if current_label in selected_labels else 0),
                    key=f"radio_{image_file}",
                    horizontal=True
                )
                if selected_label:
                    saved_selected_labels[image_file] = selected_label
                else:
                    saved_selected_labels[image_file] = ""

    st.session_state.saved_selected_labels = saved_selected_labels

def main():
    st.title("Labelling Assistant")
    
    if "label_options" not in st.session_state:
        st.session_state.label_options = []

    label_options = st.session_state.label_options

    with st.sidebar:
        directory_path = st.text_input("Enter the directory of images")
        new_label = st.text_input('Enter a new label').lower()
        if st.button("Add Label"):
            add_labels(new_label, label_options)
        
        remove_label = st.selectbox("Select a label to remove:", [""] + label_options)
        if st.button("Remove Label"):
            remove_labels(remove_label, label_options)
        
        selected_labels = st.multiselect("Select labels:", ["NO LABEL"]+label_options)

        if directory_path:
            images_per_page = 15
            total_pages, image_files = calculate_number_of_pages(directory_path, images_per_page)
            st.write(f"Total Pages: {total_pages}")
            st.write(f"Total Images: {len(image_files)}")

        if st.button("Save Changes"):
            if 'saved_selected_labels' in st.session_state:
                save_selected_labels(st.session_state.saved_selected_labels)
            st.success("Changes saved successfully.")

    if directory_path:
        st.info("Directory provided")
        images_per_page = 15
        total_pages, image_files = calculate_number_of_pages(directory_path, images_per_page)
        if total_pages > 0:
            with st.sidebar:
                selected_page = st.number_input("Go to page", min_value=1, max_value=total_pages, value=1)
                page = int(selected_page)
            display_images(image_files, directory_path, page, images_per_page, selected_labels=selected_labels)
        else:
            st.info("No images to display.")
    else:
        st.info("No directory provided.")

if __name__ == '__main__':
    main()

