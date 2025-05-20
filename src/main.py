import os
import time
import pytz
import shutil
from datetime import datetime
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
    Dropdown,
    dropdown,
)
TIMEZONES = pytz.all_timezones
def rename_and_move_files_by_year(folder_path,selected_timezone):
    tz = pytz.timezone(selected_timezone)
    # Iterate over all the files in the specified folder
    for filename in os.listdir(folder_path):
        # Get the full file path
        file_path = os.path.join(folder_path, filename)

        # Check if it's a file (skip directofries)
        if os.path.isfile(file_path):
            # Get the last modification time of the file
            mod_time = os.path.getmtime(file_path)
            dt = datetime.fromtimestamp(mod_time, tz)
            # Format the modification time as "YYYY-MM-DD-HHhMMmSS"
            #new_name_format = time.strftime("%Y-%m-%d-%Hh%Mm%S", time.localtime(mod_time))
            new_name_format = dt.strftime("%Y-%m-%d-%Hh%Mm%S")
            # Extract the year from the modification time
            #year_folder = time.strftime("%Y", time.localtime(mod_time))
            year_folder = dt.strftime("%Y")
            # Create the year folder if it doesn't exist
            year_folder_path = os.path.join(folder_path, year_folder)
            if not os.path.exists(year_folder_path):
                os.makedirs(year_folder_path)

            # Get the file extension
            _, file_extension = os.path.splitext(filename)

            # Create the new file name
            new_filename = f"{new_name_format}{file_extension}"
            new_file_path = os.path.join(year_folder_path, new_filename)

            # If the file already exists, append '-1', '-2', etc. until the name is unique
            counter = 1
            while os.path.exists(new_file_path):
                new_filename = f"{new_name_format}-{counter}{file_extension}"
                new_file_path = os.path.join(year_folder_path, new_filename)
                counter += 1

            # Move the file to the year folder with the new name
            shutil.move(file_path, new_file_path)
            print(f"Renamed and moved: {filename} -> {new_file_path}")


def main(page: Page):
    selected_timezone = Dropdown(
        label="Select Timezone",
        options=[dropdown.Option(tz) for tz in TIMEZONES],
        value="GMT"
    )

    def start_program(e):

        folder_path = directory_path.value
        timezone_choice = selected_timezone.value
        if not folder_path or folder_path=="Cancelled!":
            page.dialog = AlertDialog(title=Text("Error"), content=Text("Please select a folder first!"))
            page.dialog.open = True
            page.update()
            return

        try:
            rename_and_move_files_by_year(folder_path, timezone_choice)
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
        Row([selected_timezone]),
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
