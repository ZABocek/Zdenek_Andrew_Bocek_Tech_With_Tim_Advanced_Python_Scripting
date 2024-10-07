import os                  # Provides functions for interacting with the operating system
import json                # Allows reading and writing JSON data
import shutil              # Offers high-level file operations like copying and deleting directories
from subprocess import PIPE, run  # Used to run external commands and manage their input/output
import sys                 # Access to command-line arguments and system-specific parameters

# Constants used throughout the script
GAME_DIR_PATTERN = "game"           # Pattern to identify game directories
GAME_CODE_EXTENSION = ".go"         # File extension for Go code files
GAME_COMPILE_COMMAND = ["go", "build"]  # Command to compile Go code

def find_all_game_paths(source):
    """
    Searches the source directory for subdirectories containing the GAME_DIR_PATTERN.
    Only searches the top-level directories.
    """
    game_paths = []  # List to store paths of game directories found
    
    # Walk through the directory tree starting at 'source'
    for root, dirs, files in os.walk(source):
        for directory in dirs:
            # Check if the directory name contains the pattern (case-insensitive)
            if GAME_DIR_PATTERN in directory.lower():
                path = os.path.join(source, directory)  # Construct full path
                game_paths.append(path)                 # Add path to the list
        break  # Exit after the first level to avoid recursive traversal
    
    return game_paths  # Return the list of game directory paths

def get_name_from_paths(paths, to_strip):
    """
    Generates new directory names by stripping a specified string from the original names.
    """
    new_names = []  # List to store new directory names
    for path in paths:
        _, dir_name = os.path.split(path)             # Get the directory name from the path
        new_dir_name = dir_name.replace(to_strip, "") # Remove the 'to_strip' pattern
        new_names.append(new_dir_name)                # Add the new name to the list
        
    return new_names  # Return the list of new directory names

def create_dir(path):
    """
    Creates a directory at the specified path if it doesn't already exist.
    """
    if not os.path.exists(path):  # Check if the directory already exists
        os.mkdir(path)            # Create the directory
        
def copy_and_overwrite(source, dest):
    """
    Copies the source directory to the destination, overwriting if the destination exists.
    """
    if os.path.exists(dest):      # Check if the destination directory exists
        shutil.rmtree(dest)       # Remove the existing directory and its contents
    shutil.copytree(source, dest) # Copy the source directory to the destination

def make_json_metadata_file(path, game_dirs):
    """
    Creates a JSON file containing metadata about the processed game directories.
    """
    data = {
        "gameNames": game_dirs,             # List of new game directory names
        "numberOfGames": len(game_dirs)     # Total number of games processed
    }
    with open(path, "w") as f:              # Open the file at 'path' in write mode
        json.dump(data, f)                  # Write the JSON data to the file

def compile_game_code(path):
    """
    Searches for a Go code file in the directory and compiles it using the Go build command.
    """
    code_file_name = None  # Initialize variable to store the code file name
    for root, dirs, files in os.walk(path):
        for file in files:
            # Check if the file has the Go code extension
            if file.endswith(GAME_CODE_EXTENSION):
                code_file_name = file       # Store the file name
                break                       # Stop after finding the first Go code file
        break  # Only search the top-level directory
    
    if code_file_name is None:              # If no Go code file was found
        return                              # Exit the function
    
    # Construct the command to compile the Go code file
    command = GAME_COMPILE_COMMAND + [code_file_name]
    run_command(command, path)              # Execute the compile command in the given path
    
def run_command(command, path):
    """
    Changes the working directory to 'path' and runs the specified command.
    """
    cwd = os.getcwd()           # Save the current working directory
    os.chdir(path)              # Change to the target directory
    
    # Run the command, suppressing the output
    run(command, stdout=PIPE, stdin=PIPE, universal_newlines=True)
    
    os.chdir(cwd)               # Restore the original working directory

def main(source, target):
    """
    Main function that orchestrates the process of finding, copying, compiling,
    and generating metadata for game directories.
    """
    cwd = os.getcwd()                                 # Get the current working directory
    source_path = os.path.join(cwd, source)           # Construct the full source path
    target_path = os.path.join(cwd, target)           # Construct the full target path
    
    game_paths = find_all_game_paths(source_path)     # Find all game directories in the source
    new_game_dirs = get_name_from_paths(game_paths, "_game")  # Generate new directory names

    create_dir(target_path)                           # Create the target directory if needed
    
    # Iterate over each source game path and corresponding new directory name
    for src, dest in zip(game_paths, new_game_dirs):
        dest_path = os.path.join(target_path, dest)   # Construct the destination path
        copy_and_overwrite(src, dest_path)            # Copy the game directory to the destination
        compile_game_code(dest_path)                  # Compile any Go code in the destination directory
    
    json_path = os.path.join(target_path, "metadata.json")  # Path for the metadata file
    make_json_metadata_file(json_path, new_game_dirs)       # Generate the metadata JSON file

if __name__ == "__main__":
    # Entry point of the script when run from the command line
    args = sys.argv                              # Get command-line arguments
    if len(args) != 3:
        # Ensure exactly two arguments are provided (source and target directories)
        raise Exception("You can only pass a source and target directory.")
    
    source, target = args[1:]                    # Extract the source and target arguments
    main(source, target)                         # Call the main function with provided arguments
