from abc import ABC
from typing import Dict, List, Optional
from urllib.parse import urljoin

from requests import HTTPError, Response, Session

from .models import ApiOptions, BalanceItem, Coin


class BlockchainApi(ABC):
    """
    General class for handling blockchain API services.
    """

    coin: Coin = NotImplemented
    api_options: ApiOptions = NotImplemented

    # {request_method: request_url}
    supported_requests: Dict[str, str] = {}

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self._session = Session()

    def __del__(self):
        self._session.close()

    def get(
        self,
        request_method: str,
        headers=None,
        **req_args,
    ) -> Dict:
        """
        Call specific request method with params and return raw response.
        """
        url = self._build_request_url(request_method, **req_args)
        response = self._session.get(url, headers=headers)
        return self._check_and_get_from_response(response)

    def _build_request_url(self, request_method: str, **req_args):
        path_url = self.supported_requests.get(request_method)
        if path_url is not None:
            path_url = path_url.format(**req_args)

        return urljoin(self.api_options.base_url, path_url)

    def post(self, body=None, json=None, headers=None):
        """
        Call request using json.
        """
        response = self._session.post(
            self.api_options.base_url, data=body, json=json, headers=headers
        )
        return self._check_and_get_from_response(response)

    def _check_and_get_from_response(self, response: Response) -> Dict:
        if response.status_code != 200:
            self._raise_from_response(response)
        self._opt_raise_on_other_error(response)

        return response.json()

    @staticmethod
    def _raise_from_response(response: Response) -> None:
        try:
            response.raise_for_status()
        except HTTPError as e:
            raise ApiException(e)

    def _opt_raise_on_other_error(self, response: Response) -> None:
        # implement in child
        return

    def __repr__(self):
        return f"{self.__class__.__name__}(coin={self.coin.name})"


class IBalance(ABC):
    def get_balance(self, address: str) -> List[BalanceItem]:
        raise NotImplementedError


class ApiException(Exception):
    pass


class InvalidAddressException(ApiException):
    pass