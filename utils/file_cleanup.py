import os
import shutil


def clear_application_data():
    directories = [
        "uploads",
        "chroma_db"
    ]

    for directory in directories:
        if not os.path.exists(directory):
            continue

        for item in os.listdir(directory):
            item_path = os.path.join(
                directory,
                item
            )

            try:
                if os.path.isfile(item_path):
                    os.remove(item_path)

                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)

            except Exception as e:
                print(
                    f"Failed to delete "
                    f"{item_path}: {e}"
                )
