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


def effects_hash_to_name(
        description: str,
        effects: dict[str],
        api_name: str | None = None
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
                if scale is not None and not isinstance(effect_value, str):
                    effects_refined[effect_name] = effect_value * float(scale)

                else:
                    effects_refined[effect_name] = effect_value
            # else:
                # logging.warning(f"Cannot mapping Value in effects_hash_to_name : '{api_name}',  '{effect_name}' ,"
                #                 f"'{effect_hash_str}'")
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
    effects_mapping_refined = effects_hash_to_name(description, effects_mapping, api_name)
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


def ability_refined(ability: dict, api_name:str | None = None) -> dict:
    """
    transform ability data
    """
    description = ability.get('desc')
    icon = ability.get('icon')
    name = ability.get('name')
    variables = ability.get('variables')
    variables_2 = {
        variable.get('name'): variable.get('value')
        for variable in variables
    }
    variables_3 = effects_hash_to_name(description, variables_2, api_name)
    return {
        'icon': icon,
        'name': name,
        'description': description,
        'variable_dict': variables_3,
        'variable_list': variables,
    }


def refine_metadata_champions(champions:dict) -> dict:
    """
    transform champion data
    """
    api_name = champions.get('apiName')
    cost = champions.get('cost')
    icon = champions.get('icon')
    name = champions.get('name')
    stats = champions.get('stats')
    traits = champions.get('traits')
    ability = champions.get('ability')
    ability_2 = ability_refined(ability, api_name)
    return {
        'api_name': api_name,
        'cost': cost,
        'icon': icon,
        'name': name,
        'stats': stats,
        'traits': traits,
        'ability': ability_2
    }


def traits_effects_refined(
        description: str,
        effects: list[dict],
        api_name: str | None = None
) -> list[dict]:
    """
    transform effects
    """
    traits_effects = []
    for effect in effects:
        temp_dict = effects_hash_to_name(description=description, effects=effect, api_name=api_name)
        for k, v in temp_dict.items():
            if isinstance(v, dict):
                temp_dict[k] = effects_hash_to_name(description=description, effects=v, api_name=api_name)
        traits_effects.append(temp_dict)
    return traits_effects


def metadata_traits_transform(traits: dict) -> dict:
    """
    transform traits data
    """
    api_name = traits.get('apiName')
    description = traits.get('desc')
    effects = traits.get('effects')
    icon = traits.get('icon')
    name = traits.get('name')
    effects_refined = traits_effects_refined(description=description, effects=effects, api_name=api_name)
    return {
        'api_name' : api_name,
        'description': description,
        'effects': effects_refined,
        'icon': icon,
        'name': name
    }


def refine_metadata_set_data(set_data: dict) -> dict:
    """
    transform metadata setData
    """
    set_data_name = set_data.get('name')
    set_data_mutator = set_data.get('mutator')
    set_data_number = set_data.get('number')
    set_data_champions = set_data.get('champions')
    set_data_traits = set_data.get('traits')
    return {
        'name': set_data_name,
        'mutator': set_data_mutator,
        'number': set_data_number,
        'champions': list(map(refine_metadata_champions, set_data_champions)),
        'traits': list(map(metadata_traits_transform, set_data_traits)),
    }


def refine_metadata_sets(sets: dict) -> dict:
    """
    transform sets
    """
    champions = sets.get('champions')
    sets_name = sets.get('name')
    sets_traits = sets.get('traits')
    return {
        'name': sets_name,
        'champions': list(map(refine_metadata_champions, champions)),
        'traits': list(map(metadata_traits_transform, sets_traits)),
    }
