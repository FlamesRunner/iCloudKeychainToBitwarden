# CSV tools
import csv

# Filesystem tools
import os

# GUI tools
from PySide6 import QtWidgets, QtCore, QtGui

# Helper functions
def check_format_validity(data):
    """
    Checks the validity of the format of the data.
    
    An iCloud Keychain export should have the following format:
    - The first row should be the header row with the following columns:
        1. Title
        2. URL
        3. Username
        4. Password
        5. Notes
        6. OTPAuth
    - The remaining rows should be valid data rows with 6 columns.
    """

    # Check if the data is empty
    if len(data) == 0:
        raise ValueError("There is nothing to import.")

    # Check if the first row is the header row
    if data[0] != ['Title', 'URL', 'Username', 'Password', 'Notes', 'OTPAuth']:
        raise ValueError("The first row does not contain the expected header row for iCloud Keychain exports.")

    # Check if the remaining rows are valid data rows
    for row_id in range(1, len(data)):
        if len(data[row_id]) != 6:
            raise ValueError(f'The row with ID {row_id} is not a valid data row, as it contains {len(data[row_id])} columns instead of 6 columns.')

def open_csv_and_validate(csv_file):
    """
    Opens a CSV file and validates the format of the data.
    """
    # Check if the CSV file exists
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f'The CSV file {csv_file} does not exist.')

    # Open CSV as a list of rows
    with open(csv_file, 'r') as f:
        data = list(csv.reader(f))

    # Check the validity of the format of the data
    check_format_validity(data)

    # Return the data
    return data

def convert_data_to_list_of_dicts(data):
    """
    Converts the data to a list of dictionaries.
    """

    # Convert the CSV to a list of dictionaries
    data = [dict(zip(data[0], row)) for row in data[1:]]

    # Return the data
    return data

def export_to_bitwarden_csv(data, csv_file):
    """
    Converts the list of dictionaries to a CSV file formatted
    for BitWarden.

    The CSV file will have the following columns:
    folder,favorite,type,name,notes,fields,reprompt,login_uri,login_username,login_password,login_totp
    """

    # Define the header row
    header_row = ['folder', 'favorite', 'type', 'name', 'notes', 'fields', 'reprompt', 'login_uri', 'login_username', 'login_password', 'login_totp']

    # Define the data rows
    data_rows = [[
        '', # folder
        '', # favorite; no iCloud Keychain equivalent so leave empty
        'login', # type; always login
        row['Title'], # name
        row['Notes'], # notes
        '', # fields; no iCloud Keychain equivalent so leave empty
        '', # reprompt; no iCloud Keychain equivalent so leave empty
        row['URL'], # login_uri
        row['Username'], # login_username
        row['Password'], # login_password
        row['OTPAuth'], # login_totp
    ] for row in data]

    # Write the CSV file
    with open(csv_file, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(header_row)
        writer.writerows(data_rows)

def convert_csv_to_bitwarden(input_file, output_file):
    """
    Converts a CSV file from iCloud Keychainto a CSV file 
    formatted for BitWarden.
    """
    # Open CSV as a list of rows
    rows = open_csv_and_validate(input_file)

    # Convert the CSV to a list of dictionaries
    data = convert_data_to_list_of_dicts(rows)

    # Convert the list of dictionaries to a CSV file formatted for BitWarden
    export_to_bitwarden_csv(data, output_file)

# QT GUI for the converter
class Converter(QtWidgets.QWidget):
    # Constructor
    def __init__(self):
        # Call the parent constructor
        super().__init__()

        # Set the window title
        self.setWindowTitle('iCloud Keychain to BitWarden Converter')

        # Set the window icon
        self.setWindowIcon(QtGui.QIcon('app_icon.ico'))

        # Set variables
        self.input_file = None
        self.output_file = None
        
        # Create the widgets
        self.input_file_label = QtWidgets.QLabel('Input file: None')
        self.input_file_button = QtWidgets.QPushButton('Select input file')
        self.output_file_label = QtWidgets.QLabel('Output file: None')
        self.output_file_button = QtWidgets.QPushButton('Select output file')
        self.convert_button = QtWidgets.QPushButton('Convert')

        # Add toolbar option for acknowledgements
        self.about_button = QtWidgets.QPushButton()
        self.about_button.setText('Acknowledgements')
        self.about_button.clicked.connect(self.acknowledgements)

    def open_file_dialog(self):
        """
        Opens a file dialog to select the input file.
        """
        # Open a file dialog to select the input file
        input_file, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File', '', 'CSV Files (*.csv)')

        # Set the input file
        self.input_file = input_file

        # Get the input file name (OS-agostic)
        input_file_name = os.path.basename(self.input_file)

        # Update the input file label
        self.input_file_label.setText(f'Input file: {input_file_name}')

    def save_file_dialog(self):
        """
        Opens a file dialog to select the output file.
        """
        # Open a file dialog to select the output file
        output_file, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File', '', 'CSV Files (*.csv)')

        # Set the output file
        self.output_file = output_file

        # Get the output file name (OS-agostic)
        output_file_name = os.path.basename(self.output_file)

        # Update the output file label
        self.output_file_label.setText(f'Output file: {output_file_name}')

    def convert(self):
        """
        Converts the input file to the output file.
        """
        # Check if the input file is valid
        if self.input_file is None:
            QtWidgets.QMessageBox.warning(self, 'Warning', 'Please select an input file.')
            return

        # Check if the output file is valid
        if self.output_file is None:
            QtWidgets.QMessageBox.warning(self, 'Warning', 'Please select an output file.')
            return

        try:
            # Convert the CSV file
            convert_csv_to_bitwarden(self.input_file, self.output_file)
        except Exception as e:
            # Show an error message
            QtWidgets.QMessageBox.critical(self, 'Error', f'Error: {e}')
            return

        # Show a success message
        QtWidgets.QMessageBox.information(self, 'Success', 'The CSV file has been converted successfully.')

    def create_layout(self):
        """
        Creates the layout.

        The layout will be as follows:

        Box:
        Left column: input file label, input file button
        Right column: output file label, output file button

        Bottom row: convert button

        There is also a line drawn between the box and the bottom row,
        and between the left and right columns.
        """
        # Create the layout
        layout = QtWidgets.QVBoxLayout()

        # Create the box
        box = QtWidgets.QHBoxLayout()

        # Create the left column
        left_column_frame = QtWidgets.QFrame()
        left_column = QtWidgets.QVBoxLayout()
        left_column_frame.setLayout(left_column)
        left_column.addWidget(self.input_file_label)
        self.input_file_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        # Create the right column
        right_column_frame = QtWidgets.QFrame()
        right_column = QtWidgets.QVBoxLayout()
        right_column_frame.setLayout(right_column)
        right_column.addWidget(self.output_file_label)
        self.output_file_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        # Add the left and right columns to the box
        box.addWidget(left_column_frame)
        box.addWidget(right_column_frame)

        # Add the box to the layout
        layout.addLayout(box)

        # Add another left/right column box for the buttons
        button_box = QtWidgets.QHBoxLayout()

        # Add the input and output file buttons to the box
        button_box.addWidget(self.input_file_button)
        button_box.addWidget(self.output_file_button)

        # Add the box to the layout
        layout.addLayout(button_box)

        # Add the convert and acknowledgement buttons to the layout
        layout.addWidget(self.convert_button)
        layout.addWidget(self.about_button)

        # Set the layout
        self.setLayout(layout)

        # Add a black border around the left and right columns
        left_column_frame.setFrameShape(QtWidgets.QFrame.Shape.Box)
        left_column_frame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)

        right_column_frame.setFrameShape(QtWidgets.QFrame.Shape.Box)
        right_column_frame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)


    def acknowledgements(self):
        """
        Shows the acknowledgements.
        """

        acknowledgement_text = f'''
Acknowledgements:\n\n
PySide6, QT (https://www.qt.io/download-open-source) under the LGPL license\n\n
QT contributors and their licenses: https://doc.qt.io/qt-5/licenses-used-in-qt.html\n\n
Python (https://www.python.org/) under the PSF license\n\n
Application icon: https://www.flaticon.com/free-icons/convert
        '''

        QtWidgets.QMessageBox.about(self, 'Acknowledgements', acknowledgement_text)

def main():
    """
    Main function. Launches the converter.
    """
    
    # Create the application
    app = QtWidgets.QApplication([])

    # Create the converter
    converter = Converter()

    # Create the layout
    converter.create_layout()

    # Connect the buttons
    converter.input_file_button.clicked.connect(converter.open_file_dialog)
    converter.output_file_button.clicked.connect(converter.save_file_dialog)
    converter.convert_button.clicked.connect(converter.convert)

    # Resize the window
    converter.resize(500, 300)

    # Disable resizing
    converter.setFixedSize(converter.size())

    # Show the converter
    converter.show()

    # Run the application
    app.exec()

if __name__ == '__main__':
    main()