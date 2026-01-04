"""
Austin Zip Code to Neighborhood Name Mapping
"""

AUSTIN_NEIGHBORHOODS = {
    # Downtown & Central
    '78701': 'Downtown Austin',
    '78702': 'East Austin / Holly',
    '78703': 'West Austin / Tarrytown',
    '78704': 'South Congress / Bouldin Creek',
    '78705': 'University of Texas / Hyde Park',
    
    # North Austin
    '78717': 'Steiner Ranch',
    '78729': 'Anderson Mill / Balcones Woods',
    '78750': 'Great Hills / Arboretum',
    '78758': 'North Loop / Highland',
    '78759': 'Great Hills / Northwest Hills',
    
    # East Austin
    '78721': 'East Austin / Rosewood',
    '78722': 'East Austin / Mueller',
    '78723': 'Windsor Park / University Hills',
    '78724': 'Del Valle',
    '78741': 'East Riverside / Montopolis',
    '78744': 'Southpark Meadows',
    '78745': 'Circle C Ranch / Sunset Valley',
    
    # South Austin
    '78739': 'Barton Creek / Westlake Hills',
    '78746': 'Westlake / Rollingwood',
    '78747': 'South Austin / Slaughter Lane',
    '78748': 'Circle C / Meridian',
    '78749': 'Oak Hill / Convict Hill',
    
    # West Austin
    '78730': 'River Place / Lakeway',
    '78731': 'West Lake Hills / Northwest Hills',
    '78732': 'Lakeway / Bee Cave',
    '78733': 'Lakeway',
    '78734': 'Lakeway / Spicewood',
    '78735': 'Barton Creek',
    '78736': 'Bee Cave',
    '78737': 'Driftwood / Circle C',
    '78738': 'Bee Cave / Lakeway',
    
    # Central Austin
    '78751': 'Crestview / Brentwood',
    '78752': 'North University / Hancock',
    '78753': 'North Austin / Walnut Creek',
    '78754': 'Windsor Park',
    '78756': 'Old West Austin / Clarksville',
    '78757': 'Brentwood / Allandale',
    
    # Round Rock / Pflugerville / Cedar Park (Austin Metro)
    '78613': 'Cedar Park',
    '78641': 'Leander',
    '78660': 'Pflugerville',
    '78681': 'Round Rock',
    
    # Suburbs
    '78610': 'Buda',
    '78619': 'Del Valle',
    '78620': 'Dripping Springs / Manor',
    '78653': 'Manor',
    '78664': 'Round Rock (North)',
    '78665': 'Round Rock (Downtown)',
    '78666': 'San Marcos (North Austin metro)',
    '78676': 'Wimberley / Dripping Springs',
    '78691': 'Pflugerville (North)',
    
    # Additional Austin Area
    '78602': 'Bastrop (East metro)',
    '78612': 'Buda (South)',
    '78616': 'Driftwood',
    '78617': 'Del Valle (East)',
    '78621': 'Elgin (East metro)',
    '78626': 'Georgetown (North metro)',
    '78627': 'Georgetown',
    '78628': 'Georgetown',
    '78634': 'Hutto',
    '78640': 'Kyle',
    '78642': 'Liberty Hill',
    '78644': 'Hutto / Taylor',
    '78645': 'Leander',
    '78646': 'Leander / Cedar Park',
    '78652': 'Manchaca',
    '78654': 'McDade',
    '78656': 'Martindale',
    '78657': 'Mountain City',
    '78669': 'Spicewood',
    '78680': 'Round Rock (East)',
    '78682': 'Round Rock (West)',
    
    # Far suburbs (in dataset)
    '75203': 'Dallas area (outlier)',
    '76541': 'Killeen area (outlier)',
    '76574': 'Temple area (outlier)',
    '77098': 'Houston area (outlier)',
}

def get_neighborhood_name(zip_code):
    """Get neighborhood name from zip code, with fallback"""
    zip_str = str(zip_code)
    return AUSTIN_NEIGHBORHOODS.get(zip_str, f"Zip {zip_str}")

def add_neighborhood_names(df):
    """Add neighborhood names to a dataframe with zip_code column"""
    df['neighborhood_name'] = df['zip_code'].apply(get_neighborhood_name)
    return df
