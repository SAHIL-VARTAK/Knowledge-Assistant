from unittest.mock import patch

from utils.file_cleanup import clear_application_data


@patch("utils.file_cleanup.os.path.exists")
def test_directory_does_not_exist(mock_exists):
    mock_exists.return_value = False

    clear_application_data()

    mock_exists.assert_called_once_with("uploads")


@patch("utils.file_cleanup.os.listdir")
@patch("utils.file_cleanup.os.path.exists")
def test_empty_directory(
    mock_exists,
    mock_listdir,
):
    mock_exists.return_value = True
    mock_listdir.return_value = []

    clear_application_data()

    mock_listdir.assert_called_once_with("uploads")


@patch("utils.file_cleanup.os.remove")
@patch("utils.file_cleanup.os.path.isfile")
@patch("utils.file_cleanup.os.listdir")
@patch("utils.file_cleanup.os.path.exists")
def test_delete_file(
    mock_exists,
    mock_listdir,
    mock_isfile,
    mock_remove,
):
    mock_exists.return_value = True
    mock_listdir.return_value = ["resume.pdf"]
    mock_isfile.return_value = True

    clear_application_data()

    mock_remove.assert_called_once()


@patch("utils.file_cleanup.shutil.rmtree")
@patch("utils.file_cleanup.os.path.isdir")
@patch("utils.file_cleanup.os.path.isfile")
@patch("utils.file_cleanup.os.listdir")
@patch("utils.file_cleanup.os.path.exists")
def test_delete_directory(
    mock_exists,
    mock_listdir,
    mock_isfile,
    mock_isdir,
    mock_rmtree,
):
    mock_exists.return_value = True
    mock_listdir.return_value = ["folder"]

    mock_isfile.return_value = False
    mock_isdir.return_value = True

    clear_application_data()

    mock_rmtree.assert_called_once()


@patch("builtins.print")
@patch("utils.file_cleanup.os.remove")
@patch("utils.file_cleanup.os.path.isfile")
@patch("utils.file_cleanup.os.listdir")
@patch("utils.file_cleanup.os.path.exists")
def test_delete_exception(
    mock_exists,
    mock_listdir,
    mock_isfile,
    mock_remove,
    mock_print,
):
    mock_exists.return_value = True
    mock_listdir.return_value = ["resume.pdf"]

    mock_isfile.return_value = True
    mock_remove.side_effect = OSError("Permission denied")

    clear_application_data()

    mock_print.assert_called_once()
