usage: ducryptacy.py [-h] [--storage STORAGE] [--id ID] [--run_program RUN_PROGRAM] [--threads THREADS] repository_dir  

Use duplicacy to encrypt and decrypt sensitive files while keeping a running backup.  

positional arguments:  
  repository_dir        Directory to be encrypted.  

options:  
  -h, --help            show this help message and exit  
  --storage STORAGE     Primary storage location for backups (default: ./duplicacy/).  
  --id ID               Identifier for the primary storage (default: duplicacy).  
  --run_program RUN_PROGRAM  
                        Path to the external program to run after decryption (optional).  
  --threads THREADS     Number of threads for parallel processing (default: 4).  