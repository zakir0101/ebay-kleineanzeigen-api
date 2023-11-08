import json
import os
from pathlib import Path

from telegram.base import Base


class ImageFiles(Base):

    def __init__(self, telegram_api_url,bot_token, user_state, chat_id):
        super().__init__(telegram_api_url,bot_token, user_state, chat_id)

    def handle_image_files_menu(self):
        """
        Sends a message with options for image file management.
        """
        self.user_state['mode'] = self.MODE_IMAGE_FILE
        image_options = ["Browse Subdirectories", "Add New Subdirectory", "Back to Main Menu"]
        keyboard = self.make_file_selection_keyboard(image_options)
        self.send_message("Image Files Menu: Choose an option", reply_markup=json.dumps(keyboard))

    def handle_image_files_selection(self, selection):
        """
        Handle user's selection from the image files menu.
        """
        if selection == "Browse Subdirectories":
            self.show_subdirectories()
        elif selection == "Add New Subdirectory":
            self.add_new_subdirectory()
        elif selection == "Back to Main Menu":
            self.user_state.pop("mode", None)
            self.send_welcome_message()
        elif selection == "Back to Image Files Menu":
            self.handle_image_files_menu()
        else:
            self.user_state["subdirectory"] = selection
            self.show_images_in_subdirectory(selection)

    def show_subdirectories(self):
        """
        Show a list of subdirectories in the 'images' directory.
        """
        subdirectories = [f.name for f in Path('images').iterdir() if f.is_dir()]
        subdirectories.append("Back to Image Files Menu")
        keyboard = self.make_file_selection_keyboard(subdirectories)
        self.send_message("Select a subdirectory:", reply_markup=json.dumps(keyboard))

    def show_images_in_subdirectory(self, subdirectory):
        """
        Show a list of image files in the specified subdirectory.
        """
        image_files = os.listdir(Path('images') / subdirectory)
        # self.user_state.update({"subdirectory" : subdirectory})
        image_files.append("Add New Image")

        image_files.append("Back to Subdirectories")
        keyboard = self.make_file_selection_keyboard(image_files)
        self.send_message("Select an image file or add a new one:", reply_markup=json.dumps(keyboard))

    def handle_image_file_selection(self, subdirectory, selection):
        """
        Handle user's selection of an image file.
        """
        if selection == "Add New Image":
            self.add_new_image(subdirectory)
        elif selection == "Back to Subdirectories":
            self.user_state["subdirectory"] = None
            self.show_subdirectories()
        else:
            self.send_image_file(subdirectory, selection)
            keyboard = {
                "inline_keyboard": [
                    [{"text": "Delete Image", "callback_data": f"delete_{selection}"}],
                    [{"text": "Back to Image List", "callback_data": f"back_{subdirectory}"}]
                ]
            }
            self.send_message("Select an option:", reply_markup=json.dumps(keyboard))

    def send_image_file(self, subdirectory, image_name):
        """
        Sends the image file to the user.
        """
        image_path = Path('images') / subdirectory / image_name
        with image_path.open('rb') as image:
            self.send_photo(image_file=image)

    def add_new_subdirectory(self):
        """
        Start the process of adding a new subdirectory.
        """
        self.send_message("Please send the name for the new subdirectory.")
        self.user_state['add_subdirectory'] = True

    def handle_new_subdirectory_name(self, name):
        """
        Handles the creation of a new subdirectory with the given name.
        """
        new_path = Path('images') / name
        try:
            new_path.mkdir(parents=True, exist_ok=False)
            self.send_message(f"Subdirectory '{name}' created successfully.")
        except FileExistsError:
            self.send_message(f"Subdirectory '{name}' already exists.")
        except Exception as e:
            self.send_message(f"Failed to create subdirectory. Error: {e}")

        self.user_state.pop('add_subdirectory')
        self.show_subdirectories()

    def add_new_image(self, subdirectory):
        """
        Instructs the user to send a new image to add to the subdirectory.
        """
        self.send_message("Please send the new image file name.")
        self.user_state['add_image'] = True
        self.user_state['subdirectory'] = subdirectory

    # The method to receive the image and save it would be part of the message handler
    # outside of this class, but it would update the user state and call the necessary
    # methods to save the image to the correct subdirectory.

    def delete_image(self, subdirectory, image_name):
        """
        Deletes the specified image file from the subdirectory.
        """
        image_path = Path('images') / subdirectory / image_name
        if image_path.exists():
            image_path.unlink()  # Delete the image file
            self.send_message(f"Image '{image_name}' deleted.")
        else:
            self.send_message("Image not found.")
        self.show_images_in_subdirectory(subdirectory)

    # Remaining methods like make_file_selection_keyboard, send_message, send_photo
    # would be inherited from the Base class or implemented as needed.
    def handle_new_image_name(self,image_name):
        self.send_message("Please send the new image file (png, jpeg ..).")
        self.user_state['image_name'] = image_name


    def handle_new_image(self, file_id,image_name,subdirectory):
        file_path = self.get_file_path(file_id)
        if file_path:
            file_extension = file_path.split('.')[-1] if '.' in file_path else ''
        image_response = self.download_image(file_path)
        if image_response :
            self.save_image(image_name, file_extension, subdirectory, image_response)
            self.send_message("Image added successfully!")

        else:
            # Handle the error, perhaps set a flag or send a message that download failed.
            self.send_message("Failed to download image.")

        self.user_state.pop("add_image")
        self.user_state.pop("image_name")
        # self.user_state.pop("subdirectory")

        self.handle_image_files_selection(subdirectory)

    def save_image(self, image_name, file_ext, subdirectory, image_response):
        subdirectory_path = Path('images') / subdirectory
        subdirectory_path.mkdir(parents=True, exist_ok=True)

        image_file_name = f"{image_name}.{file_ext}"  # Replace with your logic for naming
        image_path = subdirectory_path / image_file_name

        with image_path.open('wb') as image_file:
            for chunk in image_response.iter_content(chunk_size=128):
                image_file.write(chunk)

