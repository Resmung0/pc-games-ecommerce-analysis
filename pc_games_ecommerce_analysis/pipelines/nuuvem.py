import pandas as pd
from numpy import nan


def read_data(file_path: str) -> pd.DataFrame:
    return pd.read_json(file_path, orient='records')

def correct_release_date_column(data: pd.DataFrame) -> pd.DataFrame:
    data_to_correct = {
        "Blade & Soul": '2016-01-19',
        "Disney Games Other-Worldly Pack": nan,
        "Minecraft: Java and Bedrock Edition": '2011-11-18',
        "Aquatico": '2023-12-01',
        "Banishers: Ghosts of New Eden": nan,
        "Gaucho and the Grassland": '2023-06-19',
        "Legends of Runeterra": '2020-04-29',
        "Shaiya": nan,
        "Aura Kingdom": '2013-12-23',
        "NECROPOLIS: BRUTAL EDITION": '2016-07-12',
        "Immortal Realms: Vampire Wars": '2020-08-28'
    }
    titles, release_dates = data_to_correct.items()
    titles_filter = data.title.map(lambda title: title in titles)
    return data.assign(
        release_date=data.release_date.mask(titles_filter, release_dates)
    )

def correct_os_column(data: pd.DataFrame) -> pd.DataFrame:
    corrected_os = data.os.map(
        lambda element: nan if element == 'Xbox Series S|X' else element
    )
    corrected_os['Windows' in data.drm] = 'Windows'
    return data.assign(os=corrected_os)

def correct_price_column(data: pd.DataFrame) -> pd.DataFrame:
    corrected_price = (
        data.price.pipe(lambda price: price.str.strip('R$'))
        .pipe(lambda price: price.str.replace(',', '.'))
        .pipe(lambda price: price.str.replace('Free',  '0'))
    )
    return data.assign(price=corrected_price)

def correct_drm_column(data: pd.DataFrame) -> pd.DataFrame:
    values_to_replace = {
        'Steam - Free To Play': 'Steam',
        'Microsoft - Minecraft': 'Microsoft Store',
        'Epic Games Keyless': 'Epic Games',
        'Windows': nan
    }
    return data.assign(drm=data.drm.replace(values_to_replace))

def drop_unavailable_item(data: pd.DataFrame) -> pd.DataFrame:
    labels = data.query("price == 'Unavailable'").index
    return data.drop(labels)

def drop_not_game_item(data: pd.DataFrame) -> pd.DataFrame:
    not_allowed_titles = [
        'NoPing - 30 days',
        'The Crown Stones: Mirrah - DEMO',
        'Tomb Raider Collection'
    ]
    title_filter = data.title.map(lambda title: title in not_allowed_titles)
    idx_to_drop = [
        data[title_filter].index,
        data.query("drm == 'Microsoft - Office'").index
    ]
    idx_to_drop = pd.concat(idx_to_drop, axis=0)
    return data.drop(idx_to_drop)
