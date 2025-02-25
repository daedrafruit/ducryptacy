import os
import shutil
import subprocess
import argparse
from pathlib import Path

def run_command(command, success_msg, error_msg):
    """Run a shell command and handle success/error messages."""
    try:
        result = subprocess.run(command, shell=True, check=True, text=True)
        print(success_msg)
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(error_msg)
        return e.returncode

def delete_files(repository_dir):
    """Delete all files in the repository directory after confirmation."""
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
    
    repository_dir = Path(args.repository_dir).resolve()
    storage_url = Path(args.storage).resolve()
    program_url = Path(args.run_program).resolve() if args.run_program else None
    
    init_command = f"duplicacy init -e {args.id} {storage_url}"
    encrypt_command = f"duplicacy backup -threads {args.threads}"
    
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
                run_command(init_command, "Storage initialized successfully.", "Failed to initialize storage.")
            
            case '2':  # Encrypt and Delete
                run_command(encrypt_command, "Backup successful.", "Failed to create backup.")
                delete_files(repository_dir)
            
            case '3':  # Decrypt
                run_command(init_command, "Repository initialized successfully.", "Failed to initialize repository.")
                run_command("duplicacy list", "Revisions listed successfully.", "Failed to list revisions.")
                
                revision = input("Enter the revision number to restore: ")
                run_command(f"duplicacy restore -r {revision} -overwrite", "Successfully restored", "Failed to restore.")
                
                # If a program url was passed in, run the program
                if program_url:
                    if program_url.exists() and os.access(program_url, os.X_OK):
                        print(f"Running external program: {program_url}")
                        try:
                            subprocess.run([str(program_url)], check=True)
                        except subprocess.CalledProcessError as e:
                            print(f"Failed to run the program: {str(e)}")
                            continue
                    else:
                        print(f"The program at {program_url} does not exist or is not executable. Skipping program execution.")
                        continue
                
                if program_url:
                    print("Encrypting and deleting files after program execution...")
                    run_command(encrypt_command, "Encryption successful.", "Failed to encrypt.")
                    delete_files(repository_dir)
            
            case '4':  # Encrypt
                run_command(encrypt_command, "Encryption successful.", "Failed to encrypt.")
            
            case '5':  # Restore
                run_command("duplicacy list", "Revisions listed successfully.", "Failed to list revisions.")
                revision = input("Enter the revision number to restore: ")
                run_command(f"duplicacy restore -r {revision} -overwrite", "Successfully restored", "Failed to restore.")
            
            case '6':  # Delete
                delete_files(repository_dir)
            
            case '7':  # Exit
                break
            
            case _:
                print("Invalid option. Please choose again.")
        
        print("\n")

if __name__ == "__main__":
    main()
