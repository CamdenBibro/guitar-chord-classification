

import os

def rename_chord_files(folder_path):
    try:
        # List all files in the folder
        files = os.listdir(folder_path)
        
        for file_name in files:
            # Check if it's a file (and not a folder)
            if os.path.isfile(os.path.join(folder_path, file_name)):
                # Replace '#' with 'sharp' and '+' with 'plus' in the filename
                new_file_name = file_name.replace('#', 'sharp').replace('+', 'plus')
                
                # Full path of old and new filenames
                old_file_path = os.path.join(folder_path, file_name)
                new_file_path = os.path.join(folder_path, new_file_name)
                
                # Rename the file
                os.rename(old_file_path, new_file_path)
                print(f"Renamed: {file_name} -> {new_file_name}")
        
        print("Renaming completed.")
    except Exception as e:
        print(f"Error: {e}")

# Provide the folder path where your image files are located
folder_path = "/Users/camdenbibro/Documents/Guitar-Chord-Classification/static/guitar_chords"  # Replace this with your actual folder path
rename_chord_files(folder_path)


files = os.listdir(folder_path)
print(files)
# save as a txt file
with open("guitar_chords.txt", "w") as f:
    for file in files:
        f.write(file + "\n")
        
        
        import os

CHORD_IMAGES_FOLDER = "./static/guitar_chords"

for filename in os.listdir(CHORD_IMAGES_FOLDER):
    normalized = filename.strip().replace(" ", "_").lower()
    if filename != normalized:
        os.rename(
            os.path.join(CHORD_IMAGES_FOLDER, filename),
            os.path.join(CHORD_IMAGES_FOLDER, normalized)
        )