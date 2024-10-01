import streamlit as st
import os
import json

selected_labels_file = 'selected_labels_file_videio.json'

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
            st.warning(f'There are some items labeled with "{label}".')
    elif not label:
        st.warning("Please select a label to remove.")
    else:
        st.warning("Label does not exist.")

def calculate_video_pages(directory_path, videos_per_page=15):
    files = os.listdir(directory_path)
    video_files = [f for f in files if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))]

    if not video_files:
        st.info("No videos present in this directory.")
        return 0, []

    total_pages = (len(video_files) + videos_per_page - 1) // videos_per_page
    return total_pages, video_files

def display_videos(video_files, directory_path, page, videos_per_page=15, selected_labels=None):
    start_index = (page - 1) * videos_per_page
    end_index = min(start_index + videos_per_page, len(video_files))
    current_videos = video_files[start_index:end_index]

    saved_selected_labels = load_selected_labels()

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
    st.title("Video Labeling Assistant")

    if "label_options" not in st.session_state:
        st.session_state.label_options = []

    label_options = st.session_state.label_options

    with st.sidebar:
        directory_path = st.text_input("Enter the directory of video files")
        new_label = st.text_input('Enter a new label').lower()
        if st.button("Add Label"):
            add_labels(new_label, label_options)
        
        remove_label = st.selectbox("Select a label to remove:", [""] + label_options)
        if st.button("Remove Label"):
            remove_labels(remove_label, label_options)
        
        selected_labels = st.multiselect("Select labels to use for videos:", ["NO LABEL"] + label_options)

        if directory_path:
            videos_per_page = 15
            total_pages, video_files = calculate_video_pages(directory_path, videos_per_page)
            st.write(f"Total Pages: {total_pages}")
            st.write(f"Total Videos: {len(video_files)}")

        if st.button("Save Changes"):
            if 'saved_selected_labels' in st.session_state:
                save_selected_labels(st.session_state.saved_selected_labels)
            st.success("Changes saved successfully.")

    if directory_path:
        st.info("Directory provided")
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
