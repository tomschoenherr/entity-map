from splink import SettingsCreator, Linker
import splink.comparison_library as cl
from splink import DuckDBAPI, block_on
import numpy as np
import json
import duckdb




class LinkageModel():
    """
    LinkageModel uses splink to build a probabilistic linkage model between procurement and financial records
    Use this class to train the model and predict the probability of 2 records representing the same company

    Uses multiple fuzzy matching rules and a variety of blocking setups to balance comparison number with computational time
    
    """

    def __init__(self, proc_data, fin_data):
        """
        Args:
            proc_data (pandas df): Cleaned / preprocessed procurement data
            fin_data (pandas df): Cleaned / preprocessed financial data
        Returns:
            None
        """


        duckdb.sql("SET threads=1")
        db_api = DuckDBAPI()
        self.proc_data = proc_data
        self.fin_data = fin_data

        self.blocking_rules = [
            # Highly specific blocks
            block_on("zipcode", "area_code"),
            block_on("state", "city", "area_code"),
            block_on("state", "city"),
            block_on("name", "iso"),
            block_on("street_name", "iso"),
            # Moderately specific blocks
            block_on("state", "area_code"),
            block_on("city", "area_code"),       
            block_on("city"),                    
            block_on("zipcode"),
            # General fallback blocks

            block_on("area_code"),
            block_on("LEFT(name, 8)", "iso"),
        ]
                
        settings = SettingsCreator(
            link_type = "link_only",
            blocking_rules_to_generate_predictions=self.blocking_rules,
            comparisons=[

                # name mapping (Jaro / Jaro-Winkler)
                cl.JaroWinklerAtThresholds("name", score_threshold_or_thresholds=[0.92, 0.88, 0.7]),
                cl.JaroWinklerAtThresholds("street_name", score_threshold_or_thresholds=[0.92, 0.88, 0.7]),
                cl.JaroAtThresholds('websiteurl'),

                # number linking (Damerau-Levenshtein)
                cl.DamerauLevenshteinAtThresholds("address_number"),
                cl.DamerauLevenshteinAtThresholds("zipcode").configure(term_frequency_adjustments=True),
                cl.DamerauLevenshteinAtThresholds("area_code").configure(term_frequency_adjustments=True),
                
                # location linking (exact matches)
                cl.ExactMatch("iso").configure(term_frequency_adjustments=True),
            
                ],
                probability_two_random_records_match=1/np.min([proc_data.shape[0], fin_data.shape[0]]),
                retain_intermediate_calculation_columns=True
            )

        self.linker = Linker([proc_data, fin_data], settings, db_api=db_api)

    def fit(self):
        """
        Args:
            self  (LinkageModel object)
        Returns:
            None
        """
        # estimate u (random matching probabilities) of entries
        self.linker.training.estimate_u_using_random_sampling(max_pairs=1e8)

        training_blocking_rule = block_on("state", "city")
        training_session_geo = (
            self.linker.training.estimate_parameters_using_expectation_maximisation(training_blocking_rule)
        )
        training_blocking_rule = block_on("area_code")
        training_session_area_code = self.linker.training.estimate_parameters_using_expectation_maximisation(
            training_blocking_rule
        )

    def load(self):

        with open("trained_model.json", "r") as f:
            settings = json.load(f)


        self.linker = Linker([self.proc_data, self.fin_data], settings, db_api=DuckDBAPI())

    def predict(self):
        """
        Args:
            self  (LinkageModel object)
        Returns:
            pandas dataframe (pred_df) The dataframe of predicted values. Contains all features for any comparisons needed
        """
        self.predictions = self.linker.inference.predict()
        self.pred_df = self.predictions.as_pandas_dataframe()

        return self.pred_df




