from __future__ import annotations

import os
import time
from datetime import datetime, timedelta

import pytz
import requests
from requests.adapters import HTTPAdapter, Retry

from tft.riot_api.constant import TFT_KR_BASE_HOST, TFT_ASIA_BASE_HOST, TIMEZONE, TFT_CDRAGON_LATEST_URL

API_KEY = os.environ.get('RIOT_API_TOKEN', None)
if API_KEY is None:
    raise EnvironmentError("RIOT_API_TOKEN must be initialize environment variable.")


def get_response(
        host: str,
        method: str = 'get',
        header: dict = None,
        params: dict = None,
        connect: int = 3,
        read: int = 5,
        backoff_factor: float | int = 1,
        retries_status_code: tuple[int] = (400, 403, 500, 503)
) -> requests.models.Response:
    """
    Request with retry session.
    :param host: request host
    :param method:  request method like POST, GET
    :param header: request header
    :param params: request params
    :param connect: retry connection if connection failed
    :param read: retry connection if read failed
    :param backoff_factor: A backoff factor to apply between attempts after the second try
            {backoff factor} * (2 ** ({number of total retries} - 1))
    :param retries_status_code: status code list for retries
    :return: response
    """
    requests_header = {"X-Riot-Token": API_KEY}
    if header is not None and isinstance(header, dict):
        requests_header.update(header)

    retries = Retry(
        total=(connect + read),
        connect=connect,
        read=read,
        backoff_factor=backoff_factor,
        status_forcelist=retries_status_code,
    )
    adapter = HTTPAdapter(max_retries=retries)
    with requests.Session() as session:
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        session.headers.update(requests_header)
        response = session.request(method=method, url=host, params=params)
    return response


def get_summoner_by_nickname(
        nickname: str,
        **kwargs
) -> dict:
    """
    get summoner information by nickname
    :param nickname: str for search summoner
    :return: dict object wuth summoner information
    """
    requests_host = f'{TFT_KR_BASE_HOST}/summoner/v1/summoners/by-name/{nickname}'
    response = get_response(host=requests_host, **kwargs)
    response.raise_for_status()
    return response.json()


def get_match_list(
        puuid: str,
        start_idx: int = 0,
        count: int = 20,
        start_timestamp: int = None,
        end_timestamp: int = None,
        **kwargs
) -> list[str]:
    """
    get match list by puuid
    :param puuid: summoner puuid string
    :param start_idx: search index
    :param count: count of match
    :param start_timestamp: start timestamp for search
    :param end_timestamp:  end timestamp for search
    :return: list of matchIds
    """
    requests_host = f'{TFT_ASIA_BASE_HOST}/match/v1/matches/by-puuid/{puuid}/ids'
    query_params = {
        "start": start_idx,
        "count": count,
    }
    if start_timestamp is not None:
        query_params['startTime'] = start_timestamp
    if end_timestamp is not None:
        query_params['endTime'] = end_timestamp

    response = get_response(
        host=requests_host, params=query_params, **kwargs
    )
    response.raise_for_status()
    return response.json()


def get_match_list_between_timestamp(
        puuid: str,
        start_date: datetime,
        end_date: datetime = datetime.now(pytz.timezone(TIMEZONE)),
        time_sleep_second: int | float = 1,
        **kwargs
) -> list[str]:
    """
    get summoner match list using time window
    :param puuid: summoner puuid
    :param start_date: search start date
    :param end_date: search end date, This will include the end_date.
    :param time_sleep_second: time sleep to next requests next days
    :return: list of matchIds
    """
    # daily maximum will be less then 200 so, i tried like that.
    if start_date.tzinfo is None:
        start_date = start_date.replace(tzinfo=pytz.timezone(TIMEZONE))
    timedelta_days = (end_date - start_date).days

    results = []

    for delta_i in range(timedelta_days + 1):
        start_date_temp = start_date + timedelta(days=delta_i)
        end_date_temp = start_date + timedelta(days=delta_i + 1)
        start_timestamp = int(start_date_temp.timestamp())
        end_timestamp = int(end_date_temp.timestamp())
        results.extend(
            get_match_list(
                puuid=puuid, start_timestamp=start_timestamp, end_timestamp=end_timestamp, **kwargs
            )
        )
        time.sleep(time_sleep_second)
    return results


def get_match_by_match_id(match_id: str, **kwargs) -> dict:
    """
    get match information using matchIds
    :param match_id: matchIds
    :return: json of match information
    """
    requests_host = f'{TFT_ASIA_BASE_HOST}/match/v1/matches/{match_id}'
    response = get_response(host=requests_host, **kwargs)
    response.raise_for_status()
    return response.json()


def get_match_by_match_ids(
        match_ids: list[str],
        time_sleep_second: int | float = 1,
        **kwargs
) -> list[dict]:
    """
    get match information using list of matchId
    :param match_ids: list of matchId
    :param time_sleep_second: time sleep until search next matchId search
    :return: list of matchInformation
    """
    results = []
    for match_id in match_ids:
        results.append((get_match_by_match_id(match_id, **kwargs)))
        time.sleep(time_sleep_second)
    return results


def get_tft_metadata(
        metadata_host: str = TFT_CDRAGON_LATEST_URL,
        **kwargs
) -> dict:
    """
    get metadata for tft items, units etc.
    :param metadata_host: metadata of host, default is constant TFT_CDRAGON_LATEST_URL
    :return: json for metadata
    """
    metadata = get_response(host=metadata_host, **kwargs)
    metadata.raise_for_status()
    return metadata.json()
