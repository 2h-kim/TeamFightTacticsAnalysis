from __future__ import annotations
import os
import time
import pytz
import requests
from datetime import datetime, timedelta
from requests.adapters import HTTPAdapter, Retry
from constant import TFT_KR_BASE_HOST, TFT_ASIA_BASE_HOST, TIMEZONE

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
):
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


def get_summoner_by_nickname(nickname: str, **kwargs) -> dict:
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
):
    requests_host= f'{TFT_ASIA_BASE_HOST}/match/v1/matches/by-puuid/{puuid}/ids'
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
) -> list[dict]:
    # daily maximum will be less then 200 so, i tried like that.
    if start_date.tzinfo is None:
        start_date = start_date.replace(tzinfo=pytz.timezone('Asia/Seoul'))
    timedelta_days = (end_date - start_date).days

    results = []

    for delta_i in range(timedelta_days+1):
        start_date_temp = start_date + timedelta(days=delta_i)
        end_date_temp = start_date + timedelta(days=delta_i+1)
        start_timestamp = int(start_date_temp.timestamp())
        end_timestamp = int(end_date_temp.timestamp())
        results.extend(
            get_match_list(
                puuid=puuid, start_timestamp=start_timestamp, end_timestamp=end_timestamp, **kwargs
            )
        )
        time.sleep(time_sleep_second)
    return results


def get_match_by_match_id(match_id: str, **kwargs):
    requests_host = f'{TFT_ASIA_BASE_HOST}/match/v1/matches/{match_id}'
    response = get_response(host=requests_host, **kwargs)
    response.raise_for_status()
    return response.json()


def get_match_by_match_ids(match_ids: list[str],
                           time_sleep_second: int | float = 1,
                           **kwargs):
    results = []
    for match_id in match_ids:
        results.append((get_match_by_match_id(match_id, **kwargs)))
        time.sleep(time_sleep_second)
    return results



# metadata
metadata = requests.get()
metadata_json = metadata.json()
metadata_items= metadata_json.get('items')
metadata_set_data= metadata_json.get('setData')
metadata_sets= metadata_json.get('sets')




