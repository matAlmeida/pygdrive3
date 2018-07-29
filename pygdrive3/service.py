from __future__ import print_function
from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from httplib2 import Http
from oauth2client import file, client, tools
import mimetypes
import os


class DriveService:
    def __init__(self, client_secret):

        client_secret_path = os.path.abspath(client_secret)
        has_client_secret = os.path.isfile(client_secret_path)

        if not has_client_secret:
            link = 'https://developers.google.com/drive/api/v3/quickstart/python'
            raise NameError(
                '<client_secret.json> not Found. Access the following link and go to step one to get your client_secret.json file:\n {0}'.format(link))

        self.client_secret = client_secret_path

    def auth(self):
        current_dir = os.getcwd()
        credentials_dir = os.path.join(
            current_dir, os.path.abspath('./credentials'))
        if not os.path.exists(credentials_dir):
            os.makedirs(credentials_dir)
        SCOPES = 'https://www.googleapis.com/auth/drive'
        store = file.Storage(credentials_dir + '/credentials.json')
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets(self.client_secret, SCOPES)
            creds = tools.run_flow(flow, store)
        self.drive_service = build('drive', 'v3', http=creds.authorize(Http()))

    def create_folder(self, name, parent_id=None):
        if parent_id != None:
            metadata = {
                'name': name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [parent_id]
            }
        else:
            metadata = {
                'name': name,
                'mimeType': 'application/vnd.google-apps.folder'
            }

        folder = self.drive_service.files().create(
            body=metadata,
            fields='id'
        ).execute()

        return folder.get('id')

    def upload_file(self, name, filePath, folder_id):
        fileType = mimetypes.guess_type(filePath)[0]
        if fileType == None:
            raise NameError("Invalid type or missing suffix!")

        file_metadata = {
            'name': name + '.' + fileType.split('/')[-1],
            'parents': [folder_id]
        }
        media = MediaFileUpload(filePath, mimetype=fileType)

        file = self.drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()

        return file.get('id')

    def writer_permission(self, email, file_id):
        batch = self.drive_service.new_batch_http_request(
            callback=self.__callback)
        permission = {
            'type': 'user',
            'role': 'writer',
            'emailAddress': email
        }
        batch.add(self.drive_service.permissions().create(
            fileId=file_id,
            body=permission,
            fields='id',
        ))
        batch.execute()

        return True

    def reader_permission(self, email, file_id):
        batch = self.drive_service.new_batch_http_request(
            callback=self.__callback)
        permission = {
            'type': 'user',
            'role': 'reader',
            'emailAddress': email
        }
        batch.add(self.drive_service.permissions().create(
            fileId=file_id,
            body=permission,
            fields='id',
        ))
        batch.execute()

        return True

    def transfer_ownership(self, email, file_id):
        batch = self.drive_service.new_batch_http_request(
            callback=self.__callback)
        permission = {
            'type': 'user',
            'role': 'owner',
            'emailAddress': email
        }
        batch.add(self.drive_service.permissions().create(
            transferOwnership=True,
            fileId=file_id,
            body=permission,
            fields='id',
        ))
        batch.execute()

        return True

    def anyone_permission(self, file_id):
        batch = self.drive_service.new_batch_http_request(
            callback=self.__callback)
        permission = {
            'type': 'anyone',
            'role': 'reader'
        }
        batch.add(self.drive_service.permissions().create(
            fileId=file_id,
            body=permission,
            fields='id',
        ))
        batch.execute()

        return 'https://drive.google.com/file/d/{0}/view?usp=sharing'.format(file_id)

    def list_files_from_folder_id(self, folder_id):
        itemsList = []

        page_token = None
        while True:
            response = self.drive_service.files().list(
                q="'" + folder_id + "' in parents",
                spaces='drive',
                fields='nextPageToken, files(id, name, modifiedTime, mimeType, size)',
                page_token=page_token
            ).execute()

            for file in response.get('files', []):
                # Process change
                itemsList.append({
                    'id': file.get('id'),
                    'name': file.get('name'),
                    'modifiedTime': file.get('modifiedTime'),
                    'type': file.get('mimeType'),
                    'size': file.get('size')
                })
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break

        return itemsList

    def list_folders_by_name(self, name):
        return self.__list_items_by_name(name, "mimeType = 'application/vnd.google-apps.folder'")

    def list_files_by_name(self, name):
        return self.__list_items_by_name(name, "mimeType != 'application/vnd.google-apps.folder'")

    def __list_items_by_name(self, name, extraQuery=None):
        query = 'name contains \'' + name + '\''

        if extraQuery != None:
            query += " and " + extraQuery

        print(query)
        itemsList = []

        page_token = None
        while True:
            response = self.drive_service.files().list(
                q=query,
                spaces='drive',
                fields='nextPageToken, files(id, name, modifiedTime, mimeType, size)',
                pageToken=page_token
            ).execute()

            for file in response.get('files', []):
                # Process change
                itemsList.append({
                    'id': file.get('id'),
                    'name': file.get('name'),
                    'modifiedTime': file.get('modifiedTime'),
                    'type': file.get('mimeType'),
                    'size': file.get('size')
                })
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break

        return itemsList

    def __callback(self, request_id, response, exception):
        if exception:
            # Handle error
            print(exception)
        else:
            pass
