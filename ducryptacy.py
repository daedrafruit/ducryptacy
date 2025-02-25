import os
import shutil
import subprocess
import argparse
from pathlib import Path

def run_command(command, success_msg, error_msg):
    try:
        result = subprocess.run(command, shell=True, check=True, text=True)
        print(success_msg)
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(error_msg)
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
    parser = argparse.ArgumentParser(description="Automate Duplicacy backup and restoration tasks.")
    
    parser.add_argument("--repository_dir", required=True, type=str, help="Directory to be encrypted.")
    parser.add_argument("--storage_url", type=str, default="./duplicacy/", 
                        help="Primary storage location for backups (default: ./duplicacy/).")
    parser.add_argument("--storage_id", type=str, default="duplicacy", 
                        help="Identifier for the primary storage (default: duplicacy).")
    parser.add_argument("--threads", type=int, default=1, 
                        help="Number of threads for parallel processing (default: 1).")
    
    args = parser.parse_args()
    repository_dir = Path(args.repository_dir).resolve()
    storage_url = Path(args.storage_url).resolve()

    os.chdir(repository_dir)

    while True:
        if (repository_dir / ".duplicacy").exists():
            print("WARNING: The .duplicacy file is present. The files may be unencrypted.")
        
        print("1. Init")
        print("2. Encrypt and Delete")
        print("3. Decrypt")
        print("4. Encrypt")
        print("5. Restore")
        print("6. Delete")
        print("7. Exit")
        
        choice = input("Select an option: ")
        
        match choice:
            case '1':  # Init
                init_command = f"duplicacy init -e {args.storage_id} {storage_url}"
                run_command(init_command, "Storage initialized successfully.", "Failed to initialize storage.")
            
            case '2':  # Encrypt and Delete
                encrypt_command = f"duplicacy backup -threads {args.threads}"
                run_command(encrypt_command, "Backup successful.", "Failed to create backup.")
                delete_files(repository_dir)
            
            case '3':  # Decrypt
                init_command = f"duplicacy init -e {args.storage_id} {storage_url}"
                run_command(init_command, "Repository initialized successfully.", "Failed to initialize repository.")
                run_command("duplicacy list", "Revisions listed successfully.", "Failed to list revisions.")
                revision = input("Enter the revision number to restore: ")
                restore_command = f"duplicacy restore -r {revision} -overwrite"
                run_command(restore_command, "Successfully restored", "Failed to restore.")
            
            case '4':  # Encrypt
                encrypt_command = f"duplicacy backup -threads {args.threads}"
                run_command(encrypt_command, "Encryption successful.", "Failed to encrypt.")
            
            case '5':  # Restore
                run_command("duplicacy list", "Revisions listed successfully.", "Failed to list revisions.")
                revision = input("Enter the revision number to restore: ")
                restore_command = f"duplicacy restore -r {revision} -overwrite"
                run_command(restore_command, "Successfully restored", "Failed to restore.")
            
            case '6':  # Delete
                delete_files(repository_dir)
            
            case '7':  # Exit
                break
            
            case _:
                print("Invalid option. Please choose again.")
        
        print("\n")

if __name__ == "__main__":
    main()