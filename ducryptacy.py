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

def run_program(repository_dir, storage_id, storage_url, program_url, backup_url, backup_id, threads):
    init_command = f"duplicacy init -e {storage_id} {storage_url}"
    encrypt_command = f"duplicacy backup -threads {threads}"

    add_command = None
    copy_command = None
    if backup_url:
        add_command = f"duplicacy add -copy default {backup_id} default {backup_url}"
        copy_command = f"duplicacy copy -from default -to {backup_id} -threads {threads} -key-passphrase testtest"

    run_command(init_command, "Repository initialized successfully.", "Failed to initialize repository.")
    run_command("duplicacy list", "Revisions listed successfully.", "Failed to list revisions.")
    revision = input("Enter the revision number to restore: ")
    restore_command = f"duplicacy restore -r {revision} -overwrite"
    run_command(restore_command, "Successfully restored", "Failed to restore.")
    
    if program_url:
        try:
            subprocess.run([str(program_url)], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Failed to run the program: {str(e)}")
            return
    else:
        print("No external program provided. Skipping program execution.")
    
    run_command(encrypt_command, "Encryption successful.", "Failed to encrypt.")
    
    if add_command:
        run_command(add_command, "External storage initialized.", "Failed to initialize external storage.")
    if copy_command:
        run_command(copy_command, "Backup successful.", "Failed to create backup.")
    
    delete_files(repository_dir)

def main():
    parser = argparse.ArgumentParser(description="Automate Duplicacy backup and restoration tasks.")
    
    parser.add_argument("--repository_dir", required=True, type=str, help="Directory to be encrypted.")
    
    parser.add_argument("--storage_url", type=str, default="./duplicacy/", 
                        help="Primary storage location for backups (default: ./duplicacy/).")
    parser.add_argument("--storage_id", type=str, default="duplicacy", 
                        help="Identifier for the primary storage (default: duplicacy).")
    parser.add_argument("--program_url", type=str, default=None, 
                        help="Path to the external program to run after restoration (optional).")
    parser.add_argument("--backup_url", type=str, default=None, 
                        help="Secondary storage location for backups (optional).")
    parser.add_argument("--backup_id", type=str, default=None, 
                        help="Identifier for the secondary storage (optional).")
    parser.add_argument("--threads", type=int, default=1, 
                        help="Number of threads for parallel processing (default: 1).")

    args = parser.parse_args()

    repository_dir = Path(args.repository_dir).resolve()
    storage_url = Path(args.storage_url).resolve()
    backup_url = Path(args.backup_url).resolve() if args.backup_url else None
    program_url = Path(args.program_url).resolve() if args.program_url else None

    os.chdir(repository_dir)

    while True:
        if (repository_dir / ".duplicacy").exists():
            print("WARNING: The .duplicacy file is present. The files may be unencrypted.")
        print("1. Init")
        print("2. Decrypt and Run")
        print("3. Encrypt and Delete")
        print("4. Decrypt")
        print("5. Encrypt")
        print("6. Restore")
        print("7. Delete")
        print("8. Exit")
        choice = input("Select an option: ")

        match choice:
            case '1':
                init_command = f"duplicacy init -e {args.storage_id} {storage_url}"
                run_command(init_command, "Storage initialized successfully.", "Failed to initialize storage.")
            case '2':
                run_program(
                    repository_dir,
                    args.storage_id,
                    storage_url,
                    program_url,
                    backup_url,
                    args.backup_id,
                    args.threads
                )
            case '3':
                encrypt_command = f"duplicacy backup -threads {args.threads}"
                run_command(encrypt_command, "Backup successful.", "Failed to create backup.")
                delete_files(repository_dir)
            case '4':
                init_command = f"duplicacy init -e {args.storage_id} {storage_url}"
                run_command(init_command, "Repository initialized successfully.", "Failed to initialize repository.")
                run_command("duplicacy list", "Revisions listed successfully.", "Failed to list revisions.")
                revision = input("Enter the revision number to restore: ")
                restore_command = f"duplicacy restore -r {revision} -overwrite"
                run_command(restore_command, "Successfully restored", "Failed to restore.")
            case '5':
                encrypt_command = f"duplicacy backup -threads {args.threads}"
                add_command = f"duplicacy add -copy default {args.backup_id} default {backup_url}" if backup_url else None
                copy_command = f"duplicacy copy -from default -to {args.backup_id} -threads {args.threads}" if backup_url else None
                run_command(encrypt_command, "Encryption successful.", "Failed to encrypt.")
                if add_command:
                    run_command(add_command, "External storage initialized.", "Failed to initialize external storage.")
                if copy_command:
                    run_command(copy_command, "Backup successful.", "Failed to create backup.")
            case '6':
                run_command("duplicacy list", "Revisions listed successfully.", "Failed to list revisions.")
                revision = input("Enter the revision number to restore: ")
                restore_command = f"duplicacy restore -r {revision} -overwrite"
                run_command(restore_command, "Successfully restored", "Failed to restore.")
            case '7':
                delete_files(repository_dir)
            case '8':
                break
            case _:
                print("Invalid option. Please choose again.")
        print("\n")

if __name__ == "__main__":
    main()