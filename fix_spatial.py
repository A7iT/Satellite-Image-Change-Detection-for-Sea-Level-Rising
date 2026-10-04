import pathlib
import re

path = pathlib.Path(r'D:\_Thesis\src\dataset\add_spatial_features.py')
content = path.read_text(encoding='utf-8')

# The regex matches from 'years = df["years"].unique()' down to 'continue'
pattern = r'years = df\["years"\].unique\(\).*?continue'

replacement = """periods = df[["reference_year", "comparison_year"]].drop_duplicates().values

    spatial_features_list = []

    for start_year, end_year in periods:

        logger.info(f"Processing period {start_year} -> {end_year}")

        period_df = df[
            (df["reference_year"] == start_year) & 
            (df["comparison_year"] == end_year)
        ].copy()"""

new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
path.write_text(new_content, encoding='utf-8')
print("Patched add_spatial_features.py successfully")
