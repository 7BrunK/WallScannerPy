import os

def get_files_from_folder(folder_path):
    total_paths = []
    for file_path in os.listdir(folder_path):
        total_file_path = os.path.join(folder_path, file_path)
        total_paths.append(total_file_path)
    return total_paths

print(get_files_from_folder("TestImages"))