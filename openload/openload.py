from __future__ import absolute_import

import requests

from .api_exceptions import (BadRequestException, BandwidthUsageExceeded,
                             FileNotFoundException, PermissionDeniedException,
                             ServerErrorException,
                             UnavailableForLegalReasonsException)


class OpenLoad(object):
    api_base_url = 'https://api.openload.co/{api_version}/'
    api_version = '1'

    def __init__(self, api_login, api_key):
        """Initializes OpenLoad instance with given parameters and formats api base url.

        Args:
            api_login (str): API Login found in openload.co
            api_key (str): API Key found in openload.co

        Returns:
            None
        """
        self.login = api_login
        self.key = api_key
        self.api_url = self.api_base_url.format(api_version=self.api_version)

    @classmethod
    def _check_status(cls, response_json):
        """Check the status of the incoming response, raise exception if status is not 200.

        Args:
            response_json (dict): results of the response of the GET request.

        Returns:
           None
        """
        status = response_json['status']
        msg = response_json['msg']

        if status == 400:
            raise BadRequestException(msg)
        elif status == 403:
            raise PermissionDeniedException(msg)
        elif status == 404:
            raise FileNotFoundException(msg)
        elif status == 451:
            raise UnavailableForLegalReasonsException(msg)
        elif status == 509:
            raise BandwidthUsageExceeded(msg)
        elif status >= 500:
            raise ServerErrorException(msg)

    @classmethod
    def _process_response(cls, response_json):
        """Check the incoming response, raise error if it's needed otherwise return the incoming response_json

        Args:
            response_json (dict): results of the response of the GET request.

        Returns:
            dict: results of the response of the GET request.
        """

        cls._check_status(response_json)
        return response_json['result']

    def _get(self, url, params=None):
        """Used by every other method, it makes a GET request with the given params.

        Args:
            url (str): relative path of a specific service (account_info, prepare_download, .....).
            params (dict): contains parameters to be sent in the GET request.

        Returns:
            dict: results of the response of the GET request.

        """
        if not params:
            params = {}

        params.update({'login': self.login, 'key': self.key})

        response_json = requests.get(self.api_url + url, params).json()

        # return response_json['result']
        return self._process_response(response_json)

    def account_info(self):
        """Requests everything account related (total used storage, reward, ...).

        Returns:
            dict: dictionary containing account related info.

                  {
                    "extid": "extuserid",
                    "email": "jeff@openload.io",
                    "signup_at": "2015-01-09 23:59:54",
                    "storage_left": -1,
                    "storage_used": "32922117680",
                    "traffic": {
                      "left": -1,
                      "used_24h": 0
                    },
                    "balance": 0
                  }
        """
        return self._get('account/info')

    def prepare_download(self, file_id):
        """Makes a request to prepare for file download,
        this download preparation will be used before get_download_link method.

        Args:
            file_id (str): id of the file to be downloaded.
            say we have this url "https://openload.co/f/TJNMUk2hnYs/filename", TJNMUk2hnYs is the id of this file.

        Returns:
            dict: dictionary containing response of prepare_download request.
        """
        return self._get('file/dlticket', params={'file': file_id})

    def get_download_link(self, file_id, ticket, captcha_response=None):
        """Requests direct download link for requested file,
        this method makes use of the response of prepare_download, prepare_download must be called first.

        Args:
            file_id (str): id of the file to be downloaded.

            ticket (str): preparation ticket is found in prepare_download response,
            this is why we need to call prepare_download before get_download_link.

            captcha_response (str): sometimes prepare_download will have captcha url to be solved first,
            this is the solution of the captcha.

        Returns:
            str: direct download link for the requested file.
        """
        params = {'ticket': ticket, 'file': file_id}

        if captcha_response:
            params['captcha_response'] = captcha_response

        return self._get('file/dl', params)

    def file_info(self, file_id):
        """Used to request info for a specific file, info like size, name, .....

        Args:
            file_id (str): id of the file to be downloaded.

        Returns:
            dict: dictionary containing response of file_info request.
        """
        return self._get('file/info', params={'file': file_id})

    def upload_link(self, **kwargs):
        """Makes a request to prepare for file upload.

        Args:
            **kwargs: kwargs may contain (folder: Folder-ID to upload to,
                sha1: Expected sha1 If sha1 of uploaded file doesn't match this value upload fails,
                httponly: If this is set to true, use only http upload links).

        Returns:
            dict: dictionary containing response of upload_link request.
        """
        params = {key: value for key, value in kwargs.items() if value}
        return self._get('file/ul', params=params)

    def upload_file(self, file_path, **kwargs):
        """Calls upload_link request to get valid url, then it makes a post request with given file to be uploaded.
        No need to call upload_link explicitly since upload_file calls it.

        Args:
            file_path (str): full path of the file to be uploaded.

            **kwargs: kwargs may contain (folder: Folder-ID to upload to,
                sha1: Expected sha1 If sha1 of uploaded file doesn't match this value upload fails,
                httponly: If this is set to true, use only http upload links).

        Returns:
            dict: dictionary containing response of upload_file request.
        """
        upload_url_response_json = self.upload_link(**kwargs)
        upload_url = upload_url_response_json['url']

        response_json = requests.post(upload_url,
                                      files={'upload_file': open(file_path, 'rb')}).json()

        self._check_status(response_json)
        return response_json['result']

    def remote_upload(self, remote_url, **kwargs):
        """Used to make a remote file upload to openload.co

        Args:
            remote_url (str): direct link of file to be remotely downloaded.

            **kwargs: kwargs may contain (folder: Folder-ID to upload to,
                headers: additional HTTP headers, separated by newline (e.g. Cookies or HTTP Basic-Auth)).

        Returns:
            dict: dictionary containing response data of remote_upload request.

        """
        params = {'url': remote_url}
        params.update({key: value for key, value in kwargs.items() if value})

        return self._get('remotedl/add', params=params)

    def remote_upload_status(self, **kwargs):
        """Checks a remote file upload to status.

        Args:
            **kwargs: kwargs may contain (limit: Maximum number of results (Default: 5, Maximum: 100),
                id: Remote Upload ID)

        Returns:
            dict: dictionary containing response data of remote_upload_status request.

        """
        params = {key: value for key, value in kwargs.items() if value}

        return self._get('remotedl/status', params=params)

    def list_folder(self, folder_id=None):
        """Request a list of files and folders in specified folder.

        Args:
            folder_id (str): id of the folder to be listed if not provided `Home` folder will be listed.

        Returns:
            dict: dictionary containing only two keys ("folders", "files"),
                  each key represents a list of dictionaries.

                  {
                    "folders": [
                      {
                        "id": "5144",
                        "name": ".videothumb"
                      },
                      {
                        "id": "5792",
                        "name": ".subtitles"
                      },
                      ...
                    ],
                    "files": [
                      {
                        "name": "big_buck_bunny.mp4.mp4",
                        "sha1": "c6531f5ce9669d6547023d92aea4805b7c45d133",
                        "folderid": "4258",
                        "upload_at": "1419791256",
                        "status": "active",
                        "size": "5114011",
                        "content_type": "video/mp4",
                        "download_count": "48",
                        "cstatus": "ok",
                        "link": "https://openload.co/f/UPPjeAk--30/big_buck_bunny.mp4.mp4",
                        "linkextid": "UPPjeAk--30"
                      },
                      ...
                    ]
                  }
        """
        params = {'folder': folder_id} if folder_id else {}

        return self._get('file/listfolder', params=params)

    def convert_file(self, file_id):
        """Converts previously uploaded files to a browser-streamable format (mp4 / h.264).

        Args:
            file_id (str): id of the file to be converted.

        Returns:
            bool: True if conversion started, otherwise False.

        """
        return self._get('file/convert', params={'file': file_id})

    def running_conversions(self, folder_id=None):
        """Shows running file converts by folder

        Args:
            folder_id (str): id of the folder to list conversions of files exist in it,
                             if not provided `Home` folder will be used.

        Returns:
            list: list of dictionaries, each dictionary represents a file conversion info.

                  [
                    {
                      "name": "Geysir.AVI",
                      "id": "3565411",
                      "status": "pending",
                      "last_update": "2015-08-23 19:41:40",
                      "progress": 0.32,
                      "retries": "0",
                      "link": "https://openload.co/f/f02JFG293J8/Geysir.AVI",
                      "linkextid": "f02JFG293J8"
                    },
                    ....
                  ]
        """
        params = {'folder': folder_id} if folder_id else {}
        return self._get('file/runningconverts', params=params)

    def failed_conversions(self):
        """
        Not yet implemented, openload.co said "Coming soon ...".

        Raises:
            NotImplementedError
        """
        raise NotImplementedError

    def splash_image(self, file_id):
        """Shows the video splash image (thumbnail)

        Args:
            file_id (str): id of the target file.

        Returns:
            str: url for the splash image.
        """
        return self._get('file/getsplash', params={'file': file_id})
