import os
import shutil
import subprocess
import argparse
from pathlib import Path

def run_command(command_list, success_msg, error_msg):
    try:
        print(f"Executing: {' '.join(command_list)}")
        result = subprocess.run(command_list, check=True, text=True)
        print(success_msg)
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(error_msg)
        print(f"Command output: {e.output}")
        return e.returncode

def delete_files(repository_dir):
    confirmation = input(f"Are you sure you want to delete all files in {repository_dir}? (yes/no): ")
    if confirmation.lower() == 'yes':
        try:
            shutil.rmtree(repository_dir)
            Path(repository_dir).mkdir(parents=True, exist_ok=True)
            print(f"Successfully deleted all files in: {repository_dir}")
        except Exception as e:
            print(f"An error occurred while deleting files in {repository_dir}: {str(e)}")
    else:
        print("Deletion cancelled.")

def main():
    parser = argparse.ArgumentParser(description="Use duplicacy to encrypt and decrypt sensitive files while keeping a running backup.")
    
    parser.add_argument("repository_dir", type=str, help="Directory to be encrypted.")
    parser.add_argument("--storage", type=str, default="./duplicacy/", 
                        help="Primary storage location for backups (default: ./duplicacy/).")
    parser.add_argument("--id", type=str, default="duplicacy", 
                        help="Identifier for the primary storage (default: duplicacy).")
    parser.add_argument("--run_program", type=str, default=None, 
                        help="Path to the external program to run after decryption (optional).")
    parser.add_argument("--threads", type=int, default=4, 
                        help="Number of threads for parallel processing (default: 4).")
    
    args = parser.parse_args()
    
    repository_dir = args.repository_dir
    storage_url = args.storage
    program_url = args.run_program if args.run_program else None
    
    init_command = ["duplicacy", "init", "-e", args.id, storage_url]
    encrypt_command = ["duplicacy", "backup", "-threads", str(args.threads)]
    
    os.chdir(repository_dir)
    
    while True:
        if (Path(args.repository_dir).resolve() / ".duplicacy").exists():
            print("WARNING: The .duplicacy file is present. The files may be unencrypted.")
        
        print("1. Init")
        print("2. Encrypt and Delete")
        print("3. Decrypt")
        print("4. Encrypt")
        print("5. Restore")
        print("6. Delete")
        print("7. Exit")
        
        choice = input("Select an option: ")
        
        try:
            match choice:
                case '1':  # Init
                    run_command(init_command, 
                               "Storage initialized successfully.", 
                               "Failed to initialize storage.")

                case '2':  # Encrypt and Delete
                    run_command(encrypt_command, 
                               "Backup successful.", 
                               "Failed to create backup.")
                    delete_files(repository_dir)

                case '3':  # Decrypt
                    # Initialize repository
                    run_command(init_command, 
                               "Repository initialized successfully.", 
                               "Failed to initialize repository.")

                    # List revisions
                    if run_command(["duplicacy", "list"],
                                  "Revisions listed successfully.",
                                  "Failed to list revisions.") == 0:
                        revision = input("Enter the revision number to restore: ")
                        run_command(
                            ["duplicacy", "restore", "-r", revision, "-overwrite"],
                            "Successfully restored",
                            "Failed to restore."
                        )

                    # Run external program if provided
                    if program_url:
                        print(f"Running external program: {program_url}")
                        try:
                            subprocess.run([program_url], check=True)
                        except subprocess.CalledProcessError as e:
                            print(f"Failed to run the program: {str(e)}")
                            continue

                        # Re-encrypt after program execution
                        print("Encrypting and deleting files after program execution...")
                        run_command(encrypt_command, 
                                   "Encryption successful.", 
                                   "Failed to encrypt.")
                        delete_files(repository_dir)

                case '4':  # Encrypt
                    run_command(encrypt_command, 
                               "Encryption successful.", 
                               "Failed to encrypt.")

                case '5':  # Restore
                    if run_command(["duplicacy", "list"],
                                  "Revisions listed successfully.",
                                  "Failed to list revisions.") == 0:
                        revision = input("Enter the revision number to restore: ")
                        run_command(
                            ["duplicacy", "restore", "-r", revision, "-overwrite"],
                            "Successfully restored",
                            "Failed to restore."
                        )

                case '6':  # Delete
                    delete_files(repository_dir)

                case '7':  # Exit
                    break

                case _:
                    print("Invalid option. Please choose again.")
        
        except Exception as e:
            print(f"An error occurred: {str(e)}")
        
        print("\n")

if __name__ == "__main__":
    main()
