import os
import time
import shutil
import flet
from flet import (
    ElevatedButton,
    FilePicker,
    FilePickerResultEvent,
    Page,
    Row,
    Text,
    Icons,
    AlertDialog,
    TextButton,
    MainAxisAlignment,
)
import exifread
import datetime
#from pathlib import Path

def get_photo_creation_date(file_path):
    # Open the file in binary read mode
    with open(file_path, 'rb') as f:
        # Process the EXIF data to find the original date the photo was taken
        tags = exifread.process_file(f, stop_tag='EXIF DateTimeOriginal')
        # Try to get the 'EXIF DateTimeOriginal' tag
        date_taken = tags.get('EXIF DateTimeOriginal')
        if date_taken:
            # Convert the date string from EXIF to a datetime object
            return datetime.datetime.strptime(str(date_taken), '%Y:%m:%d %H:%M:%S')
    # Return None if no date was found
    return None

def get_photo_modification_date(file_path):
    """
    Return the photo’s modification date as a `datetime.datetime` object.
    """
    try:
        return datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
    except (FileNotFoundError, OSError):
        return None

def rename_and_move_files_by_year(folder_path):
    # Loop through all files in the specified folder
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        # Check if it's a file (not a directory)
        if os.path.isfile(file_path):
            # Get the photo creation date from EXIF metadata
            creation_date = get_photo_creation_date(file_path)
            if not creation_date:
                # Fall back to filesystem modification timestamp
                creation_date = get_photo_modification_date(file_path)
                print("File without creation date,trying modification date")
                if creation_date:
                    pass
                else:
                    print("No usuable date")
                    continue  # still nothing we can use
                    # Skip the file if no EXIF creation date is found
            # Format the creation date for the new file name
            new_name_format = creation_date.strftime("%Y-%m-%d-%Hh%Mm%S")
            # Extract the year to create a year-based subfolder
            year_folder = creation_date.strftime("%Y")
            year_folder_path = os.path.join(folder_path, year_folder)
            # Create the year folder if it doesn't exist
            if not os.path.exists(year_folder_path):
                os.makedirs(year_folder_path)
            # Get the file extension
            _, file_extension = os.path.splitext(filename)
            # Generate the new file name
            new_filename = f"{new_name_format}{file_extension}"
            new_file_path = os.path.join(year_folder_path, new_filename)

            # If a file with the same name exists, add a counter to make the name unique
            counter = 1
            while os.path.exists(new_file_path):
                new_filename = f"{new_name_format}-{counter}{file_extension}"
                new_file_path = os.path.join(year_folder_path, new_filename)
                counter += 1
            # Move and rename the file to the appropriate year folder
            shutil.move(file_path, new_file_path)
            # Print a message indicating the file has been moved
            print(f"Renamed and moved: {filename} -> {new_file_path}")

def main(page: Page):

    def start_program(e):

        folder_path = directory_path.value
        if not folder_path or folder_path=="Cancelled!":
            page.dialog = AlertDialog(title=Text("Error"), content=Text("Please select a folder first!"))
            page.dialog.open = True
            page.update()
            return

        try:
            rename_and_move_files_by_year(folder_path)
            page.dialog = AlertDialog(title=Text("Success"),
                                      content=Text("Files have been renamed and moved successfully!"))
            page.dialog.open = True
            page.update()
        except Exception as e:
            page.dialog = AlertDialog(title=Text("Error"), content=Text(f"An error occurred: {e}"))
            page.dialog.open = True
            page.update()

    def handle_close(e):
        page.close(dlg_modal)
        if e.control.text == "Yes":
            # Perform the action for "Yes"
            page.add(Text("You chose to rename and move the files."))
            start_program(e)
        elif e.control.text == "No":
            # Perform the action for "No"
            page.add(Text("Action canceled."))

    dlg_modal = AlertDialog(
        modal=True,
        title=Text("Please confirm"),
        content=Text("Do you really want to rename and move all those files?"),
        actions=[
            TextButton("Yes", on_click=handle_close),
            TextButton("No", on_click=handle_close),
        ],
        actions_alignment=MainAxisAlignment.END,
    )

    # Open directory dialog
    def get_directory_result(e: FilePickerResultEvent):
        directory_path.value = e.path if e.path else "Cancelled!"
        directory_path.update()
    get_directory_dialog = FilePicker(on_result=get_directory_result)
    directory_path = Text()

    # hide all dialogs in overlay
    page.overlay.extend([get_directory_dialog])
    page.title = "File Organizer"
    page.window_width = 800
    page.window_height = 600

    page.add(
        Row(
            [
                ElevatedButton(
                    "Select directory",
                    icon=Icons.FOLDER_OPEN,
                    on_click=lambda _: get_directory_dialog.get_directory_path(),
                    disabled=page.web,
                ),
                directory_path,
            ]
        ),
        Row(
            [
                ElevatedButton(
                    "Run program",
                    icon=Icons.RUN_CIRCLE,
                    on_click=lambda e: page.open(dlg_modal),
                    disabled=page.web,
                ),
            ]
        ),
    )

flet.app(target=main)
