from __future__ import annotations

import logging
import re

from tft.common import CaseBlankInsentiveDict
from tft.riot_api.constant import DEFAULT_HASH


def refine_string_to_hash(
        string_need_to_hash: str
) -> int | str:
    """
    string to hash value
    - https://discord.com/channels/361907254997417985/361907254997417987/972945550968242197
    :param string_need_to_hash: need to change hash
    :return: int for hash string value
    """
    h = DEFAULT_HASH
    for b in string_need_to_hash.encode('ascii').lower():
        h = ((h ^ b) * 0x01000193) % 0x100000000
    return h


def item_effects_hash_to_name(
        description: str,
        effects: dict[str],
        api_name: str | None
):
    """
    effects hash mapping to name mapping
    :param description: description of item
    :param effects: effects dict
    :param api_name: api name for logging
    :return: refined effects dict
    """
    if description is None:
        return effects
    effects_pattern = r'@(.*?)@'
    effects_refined = CaseBlankInsentiveDict(effects)
    effects_from_description = re.findall(pattern=effects_pattern, string=description)
    for effect_name in effects_from_description:
        if effects_refined.get(effect_name, None) is None:
            if effect_name.find('*') != -1:
                effect_name, scale = effect_name.split('*')
            else:
                scale = None
            effect_hash = refine_string_to_hash(effect_name)
            effect_hash_str = '{' + f'{effect_hash:08x}' + '}'
            effect_value = effects_refined.get(effect_hash_str, None)
            if effect_value is not None:
                del effects_refined[effect_hash_str]
                if scale is not None:
                    effects_refined[effect_name] = effect_value * float(scale)
                else:
                    effects_refined[effect_name] = effect_value
            else:
                logging.warning(f"Cannot mapping Value in effects_hash_to_name : '{api_name}',  '{effect_name}' ,"
                                f"'{effect_hash_str}'")
    return effects_refined


def refine_metadata_item(
        metadata_item: dict
) -> dict:
    """
    transfrom item data in metadata

    :param metadata_item: metadata from riot cdragon, formed like below
        ```{
            "apiName": "TFT7_Item_MirageEmblemItem",
            "desc": "장착 시 신기루 특성 획득<br><br><tftitemrules>[고유 - 중복 적용 불가]</tftitemrules>",
            "effects": {"MagicResist": 20.0},
            "from": [6, 8],
            "icon": "ASSETS/Maps/Particles/TFT/Item_Icons/Traits/Spatula/Set7/Mirage.TFT_Set7.dds",
            "id": 2314,
            "name": "신기루 상징",
            "unique": true
        }```
    :return: dict transformed metadata items
    """
    api_name = metadata_item.get('api_name')
    description = metadata_item.get('desc')
    # description to None
    if description == "":
        description = None
    effects_mapping = metadata_item.get('effects')
    lower_items_list = metadata_item.get('from')
    icon_path = metadata_item.get('icon')
    id_ = metadata_item.get('id')
    name_ = metadata_item.get('name')
    is_unique = metadata_item.get('unique')
    effects_mapping_refined = item_effects_hash_to_name(description, effects_mapping, api_name)
    metadata_item_refined = {
        'id': id_,
        'name': name_,
        'description': description,
        'api_name': api_name,
        'icon_path': icon_path,
        'effects': effects_mapping_refined,
        'lower_items_ids': lower_items_list,
        'is_unique': is_unique
    }
    return metadata_item_refined


def refine_metadata_set_data_champions():
    # TODO sets, setData 동시에 사용해도 무관
    # TODO transform code need
    pass


def refine_metadata_set_data_traits():
    # TODO sets, setData 동시에 사용해도 무관
    # TODO transform code need
    pass


def refine_metadata_set_data(
        set_data: dict
):
    # TODO
    set_data_name = set_data.get('name')
    set_data_mutator = set_data.get('mutator')
    set_data_number = set_data.get('number')
    set_data_champions = set_data.get('champions')
    set_data_traits = set_data.get('traits')
    # TODO transform code need
    pass


def refine_metadata_sets(
        sets: dict
):
    champions = sets.get('champions')
    sets_name = sets.get('name')
    sets_traits = sets.get('traits')
    # TODO transform code need
    pass
