
from linkage_model import LinkageModel
import pandas as pd
import os
from cleaning_fx import format_finance, format_procurement





def load_data():
    """
    Args:
        None
    Returns:
        pandas df (proc_company)
        pandas df (proc_geo)
        pandas df (fin_company)
        pandas df (fin_hierarchy)
        pandas df (fin_address)

    """
    data_path = "data/"
    proc_company = pd.read_csv(os.path.join(data_path, "a__company.csv"))
    proc_geo = pd.read_csv(os.path.join(data_path, "a__geo.csv"))


    fin_company = pd.read_csv(os.path.join(data_path, "b__company.csv"))
    fin_hierarchy = pd.read_csv(os.path.join(data_path, "b__hierarchy.csv"))
    fin_address = pd.read_csv(os.path.join(data_path, "b__address.csv"))

    return proc_company, proc_geo, fin_company, fin_hierarchy,  fin_address



def main():
    proc_company, proc_geo, fin_company, fin_hierarchy, fin_address = load_data()

    print("cleaning datasets...")
    clean_proc = format_procurement(proc_company, proc_geo)
    clean_fin = format_finance(fin_company, fin_hierarchy, fin_address)

    link = LinkageModel(clean_proc, clean_fin)

    print("fitting model...")
    link.fit()
    print("model fit complete")

    print("comparing rows, this may take a few minutes")
    pred_df = link.predict()
    print("predictions complete, retaining highest probability match for vendor_id")

    # Sort by unique_id_l and match_probability (descending)
    sorted_df = pred_df.sort_values(['unique_id_l', 'match_probability'], 
                                   ascending=[True, False])
    
    # Keep only the first row (highest probability) for each vendor_id and create the final df to save
    filtered_df = sorted_df.groupby('unique_id_l').first().reset_index()
    final_df = pd.DataFrame({
    'vendor_id': filtered_df['unique_id_l'],
    'entity_id': filtered_df['unique_id_r'],
    'confidence_of_match': filtered_df['match_probability']
    })

    # Add unmatched vendor_ids from clean_proc
    all_vendor_ids = set(clean_proc['unique_id'])
    matched_vendor_ids = set(final_df['vendor_id'])
    unmatched_vendor_ids = all_vendor_ids - matched_vendor_ids

    unmatched_df = pd.DataFrame({
        'vendor_id': list(unmatched_vendor_ids),
        'entity_id': pd.NA,
        'confidence_of_match': pd.NA
    })

    # Append unmatched vendors to the final result
    final_df = pd.concat([final_df, unmatched_df], ignore_index=True)

    # Save the result as a .csv
    final_df.to_csv("linked_entities.csv", index=False)
    print("results have been saved as linked_entities.csv")



if __name__ == "__main__":
    main()