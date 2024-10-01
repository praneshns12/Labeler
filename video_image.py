import streamlit as st
import os
import json
from PIL import Image

def get_selected_labels_file(directory_path):
    parent_directory = os.path.dirname(directory_path)
    return os.path.join(parent_directory, 'selected_labels_file.json')

def load_selected_labels(directory_path):
    selected_labels_file = get_selected_labels_file(directory_path)
    if os.path.exists(selected_labels_file):
        with open(selected_labels_file, 'r') as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
            else:
                return {}
    return {}

def save_selected_labels(selected_labels, directory_path):
    selected_labels_file = get_selected_labels_file(directory_path)
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

def remove_labels(label, label_options, directory_path):
    if label and label in label_options:
        if label not in [lbl for lbl in load_selected_labels(directory_path).values()]:
            label_options.remove(label)
            st.session_state.label_options = label_options
            st.success(f"Label '{label}' removed.")
        else:
            st.warning(f'There are some items labeled with "{label}".')
    elif not label:
        st.warning("Please select a label to remove.")
    else:
        st.warning("Label does not exist.")

def rename_label(old_label, new_label, label_options, directory_path):
    if old_label in label_options:
        if new_label and new_label.lower() not in [l.lower() for l in label_options]:
            # Update label options
            label_options[label_options.index(old_label)] = new_label
            st.session_state.label_options = label_options

            # Update saved selected labels
            saved_selected_labels = load_selected_labels(directory_path)
            updated_labels = {k: (new_label if v == old_label else v) for k, v in saved_selected_labels.items()}
            st.session_state.saved_selected_labels = updated_labels
        else:
            st.warning(f"New label '{new_label}' already exists.")
    else:
        st.warning(f"Old label '{old_label}' does not exist.")

def calculate_image_pages(directory_path, images_per_page=15):
    files = os.listdir(directory_path)
    image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]

    if not image_files:
        st.info("No images present in this directory.")
        return 0, []

    total_pages = (len(image_files) + images_per_page - 1) // images_per_page
    return total_pages, image_files

def calculate_video_pages(directory_path, videos_per_page=15):
    files = os.listdir(directory_path)
    video_files = [f for f in files if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))]

    if not video_files:
        st.info("No videos present in this directory.")
        return 0, []

    total_pages = (len(video_files) + videos_per_page - 1) // videos_per_page
    return total_pages, video_files

def display_images(image_files, directory_path, page, images_per_page=15, image_size=(150, 150), selected_labels=None):
    start_index = (page - 1) * images_per_page
    end_index = min(start_index + images_per_page, len(image_files))
    current_images = image_files[start_index:end_index]

    saved_selected_labels = load_selected_labels(directory_path)

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
                    "Select label",
                    options=selected_labels,
                    index=(selected_labels.index(current_label) if current_label in selected_labels else 0),
                    key=f"radio_{image_file}"
                )
                if selected_label:
                    saved_selected_labels[image_file] = selected_label
                else:
                    saved_selected_labels[image_file] = ""

    st.session_state.saved_selected_labels = saved_selected_labels

def display_videos(video_files, directory_path, page, videos_per_page=15, selected_labels=None):
    start_index = (page - 1) * videos_per_page
    end_index = min(start_index + videos_per_page, len(video_files))
    current_videos = video_files[start_index:end_index]

    saved_selected_labels = load_selected_labels(directory_path)

    cols = st.columns(3)
    for idx, video_file in enumerate(current_videos):
        with cols[idx % 3]:
            video_path = os.path.join(directory_path, video_file)
            video_file_data = open(video_path, 'rb')
            video_bytes = video_file_data.read()
            st.video(video_bytes)

            current_label = saved_selected_labels.get(video_file, "")

            if selected_labels:
                selected_label = st.radio(
                    "Select label",
                    options=selected_labels,
                    index=(selected_labels.index(current_label) if current_label in selected_labels else 0),
                    key=f"radio_{video_file}"
                )
                if selected_label:
                    saved_selected_labels[video_file] = selected_label
                else:
                    saved_selected_labels[video_file] = ""

    st.session_state.saved_selected_labels = saved_selected_labels

def main():
    st.title("Media Labeling Assistant")

    if "label_options" not in st.session_state:
        st.session_state.label_options = []

    label_options = st.session_state.label_options

    with st.sidebar:
        directory_path = st.text_input("Enter the directory path")
        if directory_path:
            media_type = st.radio("Select media type", ("Images", "Videos"))
            
            new_label = st.text_input('Enter a new label').lower()
            if st.button("Add Label"):
                add_labels(new_label, label_options)
            
            remove_label = st.selectbox("Select a label to remove:", [""] + label_options)
            if st.button("Remove Label"):
                remove_labels(remove_label, label_options, directory_path)

            rename_old_label = st.selectbox("Select a label to rename:", [""] + label_options)
            rename_new_label = st.text_input('Enter new label name').lower()
            
            selected_labels = st.multiselect(f"Select labels to use for {media_type.lower()}:", ["NO LABEL"] + label_options)

            if media_type == "Images":
                images_per_page = 15
                total_pages, image_files = calculate_image_pages(directory_path, images_per_page)
                st.write(f"Total Pages: {total_pages}")
                st.write(f"Total Images: {len(image_files)}")
            else:
                videos_per_page = 15
                total_pages, video_files = calculate_video_pages(directory_path, videos_per_page)
                st.write(f"Total Pages: {total_pages}")
                st.write(f"Total Videos: {len(video_files)}")

            if st.button("Save Changes"):
                # Handle renaming of labels
                if rename_old_label and rename_new_label:
                    rename_label(rename_old_label, rename_new_label, label_options, directory_path)

                if 'saved_selected_labels' in st.session_state:
                    save_selected_labels(st.session_state.saved_selected_labels, directory_path)
                st.success("Changes saved successfully.")

    if directory_path:
        if media_type == "Images":
            images_per_page = 15
            total_pages, image_files = calculate_image_pages(directory_path, images_per_page)
            if total_pages > 0:
                with st.sidebar:
                    selected_page = st.number_input("Go to page", min_value=1, max_value=total_pages, value=1)
                    page = int(selected_page)
                display_images(image_files, directory_path, page, images_per_page, selected_labels=selected_labels)
            else:
                st.info("No images to display.")
        else:
            videos_per_page = 15
            total_pages, video_files = calculate_video_pages(directory_path, videos_per_page)
            if total_pages > 0:
                with st.sidebar:
                    selected_page = st.number_input("Go to page", min_value=1, max_value=total_pages, value=1)
                    page = int(selected_page)
                display_videos(video_files, directory_path, page, videos_per_page, selected_labels=selected_labels)
            else:
                st.info("No videos to display.")
    else:
        st.info("No directory provided.")

if __name__ == '__main__':
    main()
