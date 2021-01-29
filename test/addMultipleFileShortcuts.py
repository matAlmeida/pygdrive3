from context import service

drive_service = service.DriveService('.\credentials.json')
drive_service.auth()

fileURLs = open('fileURLs.txt')

for url in fileURLs:
    match = drive_service.getIdFromUrl(url)
    if match:
        shortcut = drive_service.add_file_shortcut(file_id = match[0], folder_id = '')
        print(shortcut)
