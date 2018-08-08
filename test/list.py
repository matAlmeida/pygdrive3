from context import service

drive_service = service.DriveService('./client_secret.json')
drive_service.auth()

files = drive_service.list_files_by_name('jardim atlantico')
print(files)

print('\n\n')

for file in files:
    f = drive_service.get_file_info(file['id'])
    print(f)
