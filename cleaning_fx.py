import pandas as pd
import re
import numpy as np
   
# Abbreviation mappings 
abbr_mappings = {
    # Street types
    'st': 'street',
    'str': 'street',
    'ave': 'avenue',
    'av': 'avenue',
    'blvd': 'boulevard',
    'bvd': 'boulevard',
    'boul': 'boulevard',
    'rd': 'road',
    'dr': 'drive',
    'drv': 'drive',
    'ln': 'lane',
    'ct': 'court',
    'crt': 'court',
    'pl': 'place',
    'ter': 'terrace',
    'terr': 'terrace',
    'cir': 'circle',
    'circ': 'circle',
    'pkwy': 'parkway',
    'pky': 'parkway',
    'hwy': 'highway',
    'fwy': 'freeway',
    'rte': 'route',
    'rt': 'route',
    'trl': 'trail',
    'tr': 'trail',
    'way': 'way',
    'wy': 'way',
    'sq': 'square',
    'plz': 'plaza',
    'crk': 'creek',
    'xing': 'crossing',
    'crsg': 'crossing',
    'loop': 'loop',
    'lp': 'loop',
    'walk': 'walk',
    'wlk': 'walk',
    'rdg': 'ridge',
    'rdge': 'ridge',
    'hill': 'hill',
    'hl': 'hill',
    'hls': 'hills',
    'vw': 'view',
    'vly': 'valley',
    'vlly': 'valley',
    'val': 'valley',
    'pt': 'point',
    'pte': 'point',
    'est': 'estate',
    'ests': 'estates',
    'gdn': 'garden',
    'gdns': 'gardens',
    'grn': 'green',
    'grv': 'grove',
    'hts': 'heights',
    'lndg': 'landing',
    'mdws': 'meadows',
    'pnes': 'pines',
    'shrs': 'shores',
    'spgs': 'springs',
    'sta': 'station',
    'xrd': 'crossroad',
    'xrds': 'crossroads',
    
    # Directionals
    'n': 'north',
    'no': 'north',
    'nth': 'north',
    's': 'south',
    'so': 'south',
    'sth': 'south',
    'e': 'east',
    'w': 'west',
    'wst': 'west',
    'ne': 'northeast',
    'nw': 'northwest',
    'se': 'southeast',
    'sw': 'southwest',
    
    # Address components
    'apt': 'apartment',
    'apmt': 'apartment',
    'unit': 'unit',
    'ste': 'suite',
    'su': 'suite',
    'bldg': 'building',
    'bld': 'building',
    'fl': 'floor',
    'flr': 'floor',
    'rm': 'room',
    'dept': 'department',
    'dpt': 'department',
    'lot': 'lot',
    'trlr': 'trailer',
    'frnt': 'front',
    'rear': 'rear',
    'bsmt': 'basement',
    'lbby': 'lobby',
    'ofc': 'office',
    'hngr': 'hangar',
    'pier': 'pier',
    'slip': 'slip',
    'key': 'key',
    'spc': 'space',
    
    # Business/Organization types
    'corp': 'corporation',
    'co': 'company',
    'inc': 'incorporated',
    'ltd': 'limited',
    'llc': 'limited liability company',
    'llp': 'limited liability partnership',
    'lp': 'limited partnership',
    'univ': 'university',
    'coll': 'college',
    'inst': 'institute',
    'assn': 'association',
    'assoc': 'association',
    'fed': 'federal',
    'natl': 'national',
    'intl': 'international',
    'div': 'division',
    'bur': 'bureau',
    'comm': 'commission',
    'admin': 'administration',
    'ctr': 'center',
    'cntr': 'center',
    'hosp': 'hospital',
    'med': 'medical',
    'mfg': 'manufacturing',
    'mktg': 'marketing',
    'svc': 'service',
    'svcs': 'services',
    'tech': 'technology',
    'sys': 'systems',
    'mgmt': 'management',
    'dev': 'development',
    'res': 'research',
    'fin': 'financial',
    'ins': 'insurance',
    'ent': 'enterprises',
    'grp': 'group',
    'bros': 'brothers',
    'sis': 'sisters',
    'fnd': 'foundation',
    'fdn': 'foundation',
    'tr': 'trust',
    'prop': 'properties',
    'props': 'properties',
    'rlty': 'realty',
    'inv': 'investment',
    'invs': 'investments',
    'hldg': 'holding',
    'hldgs': 'holdings',
    'cap': 'capital',
    'eq': 'equity',
    'sec': 'securities',
    'fund': 'fund',
    'acq': 'acquisition',
    'merch': 'merchant',
    'dist': 'distribution',
    'distrib': 'distribution',
    'whlsl': 'wholesale',
    'ret': 'retail',
    'mkt': 'market',
    'mkts': 'markets',
    'prod': 'products',
    'prods': 'products',
    'sol': 'solutions',
    'sols': 'solutions'
}


def remove_abbreviations_and_full_forms(text, abbreviation_dict):
    """
    Remove both abbreviated and full forms of words from a text string.
    Creates a set of all words to remove (both keys and values from the mapping).
    """
    if pd.isna(text):
        return text
    
    text_str = str(text).lower()
    
    # Create a set of all words to remove (both abbreviations and their full forms)
    words_to_remove = set()
    for abbr, full_form in abbreviation_dict.items():
        words_to_remove.add(abbr)
        words_to_remove.add(full_form)
    
    # Split into words and keep only words that are NOT in our removal set
    words = text_str.split()
    cleaned_words = []
    
    for word in words:
        # Keep the word only if it's NOT in our removal set
        if word not in words_to_remove:
            cleaned_words.append(word)
    
    return ' '.join(cleaned_words)


def remove_duplicates(df, id_col='b_entity_id'):
    """
    Remove duplicate rows based on id_col, keeping the row with least missing data.
    """
    # Count missing values for each row
    df['missing_count'] = df.isnull().sum(axis=1)
    
    # Sort by id_col and missing_count (ascending), so best row comes first for each group
    df_sorted = df.sort_values([id_col, 'missing_count'])
    
    # Keep only the first row for each b_entity_id (which has least missing data)
    df_deduplicated = df_sorted.drop_duplicates(subset=[id_col], keep='first')
    
    # Remove the helper column
    df_deduplicated = df_deduplicated.drop(columns=['missing_count'])
    
    return df_deduplicated


def extract_address_parts(address):
    """Extract address number and street name from a single address string."""
    if pd.isna(address) or address == '':
        return np.nan, np.nan
    
    address_str = str(address).strip()
    match = re.match(r'^(\d+[A-Za-z]?(?:[-/]\d+[A-Za-z]?)*(?:\s+\d+/\d+)?)\s+(.+)$', address_str)
    
    if match:
        number_part = match.group(1).strip()
        street_part = match.group(2).strip()
        return number_part, street_part
    else:
        return np.nan, address_str

def split_address(df, address_col='address', number_col='address_number', street_col='street_name'):
    """Split an address column into address number and street name."""
    df_copy = df.copy()
    df_copy[[number_col, street_col]] = df_copy[address_col].apply(
        lambda x: pd.Series(extract_address_parts(x))
    )
    return df_copy



def clean_df(df):
    """
    Clean and standardize dataframe columns for entity matching.
    Removes special characters first, then removes abbreviations and their full forms.
    """
    
    # Create a copy to avoid modifying the original
    clean_df = df.copy()
    
    # Process each column based on its data type
    for col in clean_df.columns:
        
        if col == "unique_id":
            continue 

        # Get the column's data type
        dtype = clean_df[col].dtype
        
        # Process string columns
        if dtype == 'object':
            # Step 1: Convert to string (handles any non-string objects)
            clean_df[col] = clean_df[col].astype(str)
            
            # Step 2: Replace 'nan' strings with actual NaN values
            clean_df[col] = clean_df[col].replace('nan', np.nan)
                
            # Step 3: Trim whitespace
            clean_df[col] = clean_df[col].str.strip()
            
            # Step 4: Remove special characters FIRST (keeping spaces, letters, numbers)
            clean_df[col] = clean_df[col].str.replace(r'[^\w\s]', '', regex=True)
            
            # Step 5: Remove abbreviations and their full forms AFTER special character removal
            clean_df[col] = clean_df[col].apply(
                lambda x: remove_abbreviations_and_full_forms(x, abbr_mappings)
            )
            
            # Step 6: Clean up extra whitespace that might result from removals
            clean_df[col] = clean_df[col].str.replace(r'\s+', ' ', regex=True).str.strip()

    clean_df = remove_duplicates(clean_df, id_col = 'unique_id')

    clean_df = split_address(clean_df, address_col='address', number_col='address_number', street_col='street_name')

    clean_df['area_code'] = clean_df['area_code'].str[:3]
               
    return clean_df


def format_procurement(company_df, geo_df):
    """
    Formats procurement data 
    """

    company_df['zipcode'] = company_df['zipcode'].replace(['0', 0], np.nan)
    
    data_df = pd.merge(left = company_df,
                  right = geo_df,
                  on='geo_id',
                  how = 'left')
    
    # Combine zipcodes with preference for zipcode_x, fallback to zipcode_y
    data_df['zipcode'] = data_df['zipcode_x'].fillna(data_df['zipcode_y'])

    data_df.rename(columns={"country_iso2": "iso", 'parent_vendor_id': 'parent_id', 'top_vendor_id': 'top_id', 
                           "vendor_id": "unique_id"}, inplace=True)

    df_clean = clean_df(data_df)

    used_columns = ['unique_id', 'name', 'iso', 'state', 'city', 'zipcode', 'address_number', 'street_name', 'websiteurl', 'area_code']
    df_clean = df_clean[used_columns]

    return df_clean

def format_finance(company_df, hierarchy_df, address_df):
    """
    Formats finance data
    """

    # merge hierarchy_df and company_df by the b_entity_id
    data_df = pd.merge(left = hierarchy_df,
                    right = company_df,
                    on='b_entity_id',
                    how = 'left')
    
    # combine the address columns
    address_df['address'] = (
    address_df['location_street1'].fillna('') + ' ' + 
    address_df['location_street2'].fillna('') + ' ' + 
    address_df['location_street3'].fillna('')
    ).str.strip()

    # merge data_df and address_df by the b_entity_id
    data_df = pd.merge(left = data_df,
                  right = address_df,
                  on='b_entity_id',
                  how = 'left')

    # rename columns to common formating
    data_df.rename(columns = {"b_entity_id": "unique_id","entity_name": "name", 'web_site': 'websiteurl',
                                'b_parent_entity_id': 'parent_id', "tele_area": "area_code",
                            'b_ultimate_parent_entity_id': 'top_id', "tele_full": "phone", "location_city": "city"},
                                inplace=True)

    # combine duplicate columns 
    data_df['iso'] = data_df['iso_country_x'].fillna(data_df['iso_country_y'])
    data_df['state'] = data_df['state_province_x'].fillna(data_df['state_province_y'])
    data_df['zipcode'] = data_df['zip_postal_code'].fillna(data_df['location_postal_code'])

    df_clean = clean_df(data_df)

    return df_clean