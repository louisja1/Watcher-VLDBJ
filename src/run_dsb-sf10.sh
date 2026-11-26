# echo "04/20 Q013a-6B 1 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 precompute_truecards1d.py ../input_configs/dsb_sf10_precompute_config_Q013a-6B.json
# echo "04/20 Q013a-6B 2 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 execute_trainingset1d.py ../input_configs/dsb_sf10_trainingset_config_Q013a-6B.json
# echo "04/20 Q013a-6B 3 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 truecard_main1d.py ../input_configs/dsb_sf10_true-card_config_Q013a-6B.json
# echo "04/20 Q013a-6B 4-------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 base_main1d.py ../input_configs/dsb_sf10_no-retrain_no-cache_config_Q013a-6B.json
# echo "04/20 Q013a-6B 5 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 baseline1d.py ../input_configs/dsb_sf10_baseline_config_Q013a-6B_rt1.json
# echo "04/20 Q013a-6B 6 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 baseline1d.py ../input_configs/dsb_sf10_baseline_config_Q013a-6B_rt3.json
# echo "04/20 Q013a-6B 7 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 baseline1d.py ../input_configs/dsb_sf10_baseline_config_Q013a-6B_rt6.json
# echo "04/22 Q013a-6B 8 ---------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 twotier_main1d.py ../input_configs/dsb_sf10_twotier_config_Q013a-6B.json
# echo "04/22 Q013a-6B 9 ---------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 twotier_main1d.py ../input_configs/dsb_sf10_twotier_config_Q013a-6B_correctjoin2.json


# echo "04/25 Q013b-6B 1 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 precompute_truecards1d.py ../input_configs/dsb_sf10_precompute_config_Q013b-6B.json
# echo "04/25 Q013b-6B 2 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 execute_trainingset1d.py ../input_configs/dsb_sf10_trainingset_config_Q013b-6B.json


# echo "04/25 Q100-6B 1 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 precompute_truecards1d.py ../input_configs/dsb_sf10_precompute_config_Q100-6B.json
# echo "04/25 Q100-6B 2 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 execute_trainingset1d.py ../input_configs/dsb_sf10_trainingset_config_Q100-6B.json


# echo "04/26 Q013b-6B 3 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 truecard_main1d.py ../input_configs/dsb_sf10_true-card_config_Q013b-6B.json
# echo "04/26 Q013b-6B 4-------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 base_main1d.py ../input_configs/dsb_sf10_no-retrain_no-cache_config_Q013b-6B.json
# echo "04/26 Q013b-6B 5 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 baseline1d.py ../input_configs/dsb_sf10_baseline_config_Q013b-6B_rt1.json
# echo "04/26 Q013b-6B 6 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 baseline1d.py ../input_configs/dsb_sf10_baseline_config_Q013b-6B_rt3.json
# echo "04/26 Q013b-6B 7 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 baseline1d.py ../input_configs/dsb_sf10_baseline_config_Q013b-6B_rt6.json
# echo "04/26 Q013b-6B 8 ---------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 twotier_main1d.py ../input_configs/dsb_sf10_twotier_config_Q013b-6B.json
# echo "04/26 Q013b-6B 9 ---------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 twotier_main1d.py ../input_configs/dsb_sf10_twotier_config_Q013b-6B_correctjoin2.json


# echo "04/26 Q100-6B 3 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 truecard_main1d.py ../input_configs/dsb_sf10_true-card_config_Q100-6B.json
# echo "04/26 Q100-6B 4-------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 base_main1d.py ../input_configs/dsb_sf10_no-retrain_no-cache_config_Q100-6B.json
# echo "04/26 Q100-6B 5 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 baseline1d.py ../input_configs/dsb_sf10_baseline_config_Q100-6B_rt1.json
# echo "04/26 Q100-6B 6 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 baseline1d.py ../input_configs/dsb_sf10_baseline_config_Q100-6B_rt3.json
# echo "04/26 Q100-6B 7 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 baseline1d.py ../input_configs/dsb_sf10_baseline_config_Q100-6B_rt6.json
# echo "04/26 Q100-6B 8 ---------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 twotier_main1d.py ../input_configs/dsb_sf10_twotier_config_Q100-6B.json
# echo "04/26 Q100-6B 9 ---------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 twotier_main1d.py ../input_configs/dsb_sf10_twotier_config_Q100-6B_correctjoin2.json


# echo "04/22 Q102-6B 1 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 precompute_truecards1d.py ../input_configs/dsb_sf10_precompute_config_Q102-6B.json
# echo "04/22 Q102-6B 2 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 execute_trainingset1d.py ../input_configs/dsb_sf10_trainingset_config_Q102-6B.json
# echo "04/22 Q102-6B 3 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 truecard_main1d.py ../input_configs/dsb_sf10_true-card_config_Q102-6B.json
# echo "04/22 Q102-6B 4-------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 base_main1d.py ../input_configs/dsb_sf10_no-retrain_no-cache_config_Q102-6B.json
# echo "04/20 Q102-6B 5 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 baseline1d.py ../input_configs/dsb_sf10_baseline_config_Q102-6B_rt1.json
# echo "04/20 Q102-6B 6 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 baseline1d.py ../input_configs/dsb_sf10_baseline_config_Q102-6B_rt3.json
# echo "04/20 Q102-6B 7 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 baseline1d.py ../input_configs/dsb_sf10_baseline_config_Q102-6B_rt6.json
# echo "04/22 Q102-6B 8 ---------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 twotier_main1d.py ../input_configs/dsb_sf10_twotier_config_Q102-6B.json
# echo "04/22 Q102-6B 9 ---------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 twotier_main1d.py ../input_configs/dsb_sf10_twotier_config_Q102-6B_correctjoin2.json


# echo "04/22 Q019-6B 1 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 precompute_truecards1d.py ../input_configs/dsb_sf10_precompute_config_Q019-6B.json
# echo "04/22 Q019-6B 2 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 execute_trainingset1d.py ../input_configs/dsb_sf10_trainingset_config_Q019-6B.json
# echo "04/22 Q019-6B 3 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 truecard_main1d.py ../input_configs/dsb_sf10_true-card_config_Q019-6B.json
# echo "04/22 Q019-6B 4-------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 base_main1d.py ../input_configs/dsb_sf10_no-retrain_no-cache_config_Q019-6B.json
# echo "04/20 Q019-6B 5 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 baseline1d.py ../input_configs/dsb_sf10_baseline_config_Q019-6B_rt1.json
# echo "04/20 Q019-6B 6 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 baseline1d.py ../input_configs/dsb_sf10_baseline_config_Q019-6B_rt3.json
# echo "04/20 Q019-6B 7 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 baseline1d.py ../input_configs/dsb_sf10_baseline_config_Q019-6B_rt6.json
# echo "04/22 Q019-6B 8 ---------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 twotier_main1d.py ../input_configs/dsb_sf10_twotier_config_Q019-6B.json
# echo "04/22 Q019-6B 9 ---------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 twotier_main1d.py ../input_configs/dsb_sf10_twotier_config_Q019-6B_correctjoin2.json


# echo "04/25 Q099-6B 1 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 precompute_truecards1d.py ../input_configs/dsb_sf10_precompute_config_Q099-6B.json
# echo "04/25 Q099-6B 2 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 execute_trainingset1d.py ../input_configs/dsb_sf10_trainingset_config_Q099-6B.json
# echo "04/26 Q099-6B 3 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 truecard_main1d.py ../input_configs/dsb_sf10_true-card_config_Q099-6B.json
# echo "04/26 Q099-6B 4-------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 base_main1d.py ../input_configs/dsb_sf10_no-retrain_no-cache_config_Q099-6B.json
# echo "04/26 Q099-6B 5 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 baseline1d.py ../input_configs/dsb_sf10_baseline_config_Q099-6B_rt1.json
# echo "04/26 Q099-6B 6 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 baseline1d.py ../input_configs/dsb_sf10_baseline_config_Q099-6B_rt3.json
# echo "04/26 Q099-6B 7 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 baseline1d.py ../input_configs/dsb_sf10_baseline_config_Q099-6B_rt6.json
# echo "04/26 Q099-6B 8 ---------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 twotier_main1d.py ../input_configs/dsb_sf10_twotier_config_Q099-6B.json
# echo "04/26 Q099-6B 9 ---------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 twotier_main1d.py ../input_configs/dsb_sf10_twotier_config_Q099-6B_correctjoin2.json


# echo "04/25 Q101-6B 1 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 precompute_truecards1d.py ../input_configs/dsb_sf10_precompute_config_Q101-6B.json
# echo "04/25 Q101-6B 2 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 execute_trainingset1d.py ../input_configs/dsb_sf10_trainingset_config_Q101-6B.json
# echo "04/26 Q101-6B 3 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 truecard_main1d.py ../input_configs/dsb_sf10_true-card_config_Q101-6B.json
# echo "04/26 Q101-6B 4-------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 base_main1d.py ../input_configs/dsb_sf10_no-retrain_no-cache_config_Q101-6B.json
# echo "04/26 Q101-6B 5 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 baseline1d.py ../input_configs/dsb_sf10_baseline_config_Q101-6B_rt1.json
# echo "04/26 Q101-6B 6 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 baseline1d.py ../input_configs/dsb_sf10_baseline_config_Q101-6B_rt3.json
# echo "04/26 Q101-6B 7 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 baseline1d.py ../input_configs/dsb_sf10_baseline_config_Q101-6B_rt6.json
# echo "04/26 Q101-6B 8 ---------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 twotier_main1d.py ../input_configs/dsb_sf10_twotier_config_Q101-6B.json
# echo "04/26 Q101-6B 9 ---------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 twotier_main1d.py ../input_configs/dsb_sf10_twotier_config_Q101-6B_correctjoin2.json

# echo "04/20 Q040-6B 1 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 precompute_truecards1d.py ../input_configs/dsb_sf10_precompute_config_Q040-6B.json
# echo "04/20 Q040-6B 2 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 execute_trainingset1d.py ../input_configs/dsb_sf10_trainingset_config_Q040-6B.json
# echo "04/24 Q040-6B 3 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 truecard_main1d.py ../input_configs/dsb_sf10_true-card_config_Q040-6B.json
# echo "04/24 Q040-6B 4-------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 base_main1d.py ../input_configs/dsb_sf10_no-retrain_no-cache_config_Q040-6B.json
# echo "04/24 Q040-6B 5 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 baseline1d.py ../input_configs/dsb_sf10_baseline_config_Q040-6B_rt1.json
# echo "04/24 Q040-6B 6 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 baseline1d.py ../input_configs/dsb_sf10_baseline_config_Q040-6B_rt3.json
# echo "04/24 Q040-6B 7 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 baseline1d.py ../input_configs/dsb_sf10_baseline_config_Q040-6B_rt6.json
# echo "04/24 Q040-6B 8 ---------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 twotier_main1d.py ../input_configs/dsb_sf10_twotier_config_Q040-6B.json
# echo "04/24 Q040-6B 9 ---------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 twotier_main1d.py ../input_configs/dsb_sf10_twotier_config_Q040-6B_correctjoin2.json


# echo "04/25 Q018-6B 1 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 precompute_truecards1d.py ../input_configs/dsb_sf10_precompute_config_Q018-6B.json
# echo "04/25 Q018-6B 2 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 execute_trainingset1d.py ../input_configs/dsb_sf10_trainingset_config_Q018-6B.json
# echo "04/26 Q018-6B 3 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 truecard_main1d.py ../input_configs/dsb_sf10_true-card_config_Q018-6B.json
# echo "04/26 Q018-6B 4-------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 base_main1d.py ../input_configs/dsb_sf10_no-retrain_no-cache_config_Q018-6B.json
# echo "04/26 Q018-6B 5 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 baseline1d.py ../input_configs/dsb_sf10_baseline_config_Q018-6B_rt1.json
# echo "04/26 Q018-6B 6 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 baseline1d.py ../input_configs/dsb_sf10_baseline_config_Q018-6B_rt3.json
# echo "04/26 Q018-6B 7 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 baseline1d.py ../input_configs/dsb_sf10_baseline_config_Q018-6B_rt6.json
# echo "04/24 Q018-6B 8 ---------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 twotier_main1d.py ../input_configs/dsb_sf10_twotier_config_Q018-6B.json
# echo "04/24 Q018-6B 9 ---------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 twotier_main1d.py ../input_configs/dsb_sf10_twotier_config_Q018-6B_correctjoin2.json

# echo "04/25 Q072-6B 1 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 precompute_truecards1d.py ../input_configs/dsb_sf10_precompute_config_Q072-6B.json
# echo "04/25 Q072-6B 2 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 execute_trainingset1d.py ../input_configs/dsb_sf10_trainingset_config_Q072-6B.json
# echo "04/26 Q072-6B 3 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 truecard_main1d.py ../input_configs/dsb_sf10_true-card_config_Q072-6B.json
# echo "04/26 Q072-6B 4-------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 base_main1d.py ../input_configs/dsb_sf10_no-retrain_no-cache_config_Q072-6B.json
# echo "04/26 Q072-6B 5 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 baseline1d.py ../input_configs/dsb_sf10_baseline_config_Q072-6B_rt1.json
# echo "04/26 Q072-6B 6 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 baseline1d.py ../input_configs/dsb_sf10_baseline_config_Q072-6B_rt3.json
# echo "04/26 Q072-6B 7 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 baseline1d.py ../input_configs/dsb_sf10_baseline_config_Q072-6B_rt6.json
# echo "04/24 Q072-6B 8 ---------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 twotier_main1d.py ../input_configs/dsb_sf10_twotier_config_Q072-6B.json
# echo "04/24 Q072-6B 9 ---------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 twotier_main1d.py ../input_configs/dsb_sf10_twotier_config_Q072-6B_correctjoin2.json


# echo "04/25 Q085a-6B 1 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 precompute_truecards1d.py ../input_configs/dsb_sf10_precompute_config_Q085a-6B.json
# echo "04/25 Q085a-6B 2 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 execute_trainingset1d.py ../input_configs/dsb_sf10_trainingset_config_Q085a-6B.json
# echo "04/26 Q085a-6B 3 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 truecard_main1d.py ../input_configs/dsb_sf10_true-card_config_Q085a-6B.json
# echo "04/26 Q085a-6B 4-------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 base_main1d.py ../input_configs/dsb_sf10_no-retrain_no-cache_config_Q085a-6B.json
# echo "04/26 Q085a-6B 5 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 baseline1d.py ../input_configs/dsb_sf10_baseline_config_Q085a-6B_rt1.json
# echo "04/26 Q085a-6B 6 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 baseline1d.py ../input_configs/dsb_sf10_baseline_config_Q085a-6B_rt3.json
# echo "04/26 Q085a-6B 7 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 baseline1d.py ../input_configs/dsb_sf10_baseline_config_Q085a-6B_rt6.json
# echo "04/26 Q085a-6B 8 ---------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 twotier_main1d.py ../input_configs/dsb_sf10_twotier_config_Q085a-6B.json

# echo "04/25 Q085b-6B 1 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 precompute_truecards1d.py ../input_configs/dsb_sf10_precompute_config_Q085b-6B.json
# echo "04/25 Q085b-6B 2 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 execute_trainingset1d.py ../input_configs/dsb_sf10_trainingset_config_Q085b-6B.json
# echo "04/26 Q085b-6B 3 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 truecard_main1d.py ../input_configs/dsb_sf10_true-card_config_Q085b-6B.json
# echo "04/26 Q085b-6B 4-------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 base_main1d.py ../input_configs/dsb_sf10_no-retrain_no-cache_config_Q085b-6B.json
# echo "04/26 Q085b-6B 5 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 baseline1d.py ../input_configs/dsb_sf10_baseline_config_Q085b-6B_rt1.json
# echo "04/26 Q085b-6B 6 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 baseline1d.py ../input_configs/dsb_sf10_baseline_config_Q085b-6B_rt3.json
# echo "04/26 Q085b-6B 7 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 baseline1d.py ../input_configs/dsb_sf10_baseline_config_Q085b-6B_rt6.json
# echo "04/26 Q085b-6B 8 ---------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 twotier_main1d.py ../input_configs/dsb_sf10_twotier_config_Q085b-6B.json

# echo "04/26 Q085a-6B 9 ---------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 leo_main1d.py ../input_configs/dsb_sf10_leo_config_Q085a-6B.json
# echo "04/26 Q085a-6B 10 ---------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 main1d.py ../input_configs/dsb_sf10_config_Q085a-6B.json

echo "05/09 1 -------"
dropdb -p 5555 watcherdb
createdb -p 5555 -U ANONYMOUS watcherdb
python3 pg_main1d.py ../input_configs/dsb_sf10_pg_config_Q013a-6B.json
echo "05/09 2 -------"
dropdb -p 5555 watcherdb
createdb -p 5555 -U ANONYMOUS watcherdb
python3 pg_main1d.py ../input_configs/dsb_sf10_pg_config_Q013b-6B.json
echo "05/09 3 -------"
dropdb -p 5555 watcherdb
createdb -p 5555 -U ANONYMOUS watcherdb
python3 pg_main1d.py ../input_configs/dsb_sf10_pg_config_Q018-6B.json
echo "05/09 4 -------"
dropdb -p 5555 watcherdb
createdb -p 5555 -U ANONYMOUS watcherdb
python3 pg_main1d.py ../input_configs/dsb_sf10_pg_config_Q019-6B.json
echo "05/09 5 -------"
dropdb -p 5555 watcherdb
createdb -p 5555 -U ANONYMOUS watcherdb
python3 pg_main1d.py ../input_configs/dsb_sf10_pg_config_Q040-6B.json
echo "05/09 6 -------"
dropdb -p 5555 watcherdb
createdb -p 5555 -U ANONYMOUS watcherdb
python3 pg_main1d.py ../input_configs/dsb_sf10_pg_config_Q072-6B.json
echo "05/09 7 -------"
dropdb -p 5555 watcherdb
createdb -p 5555 -U ANONYMOUS watcherdb
python3 pg_main1d.py ../input_configs/dsb_sf10_pg_config_Q085a-6B.json
echo "05/09 8 -------"
dropdb -p 5555 watcherdb
createdb -p 5555 -U ANONYMOUS watcherdb
python3 pg_main1d.py ../input_configs/dsb_sf10_pg_config_Q085b-6B.json
echo "05/09 9 -------"
dropdb -p 5555 watcherdb
createdb -p 5555 -U ANONYMOUS watcherdb
python3 pg_main1d.py ../input_configs/dsb_sf10_pg_config_Q099-6B.json
echo "05/09 10 -------"
dropdb -p 5555 watcherdb
createdb -p 5555 -U ANONYMOUS watcherdb
python3 pg_main1d.py ../input_configs/dsb_sf10_pg_config_Q100-6B.json
echo "05/09 11 -------"
dropdb -p 5555 watcherdb
createdb -p 5555 -U ANONYMOUS watcherdb
python3 pg_main1d.py ../input_configs/dsb_sf10_pg_config_Q101-6B.json
echo "05/09 12 -------"
dropdb -p 5555 watcherdb
createdb -p 5555 -U ANONYMOUS watcherdb
python3 pg_main1d.py ../input_configs/dsb_sf10_pg_config_Q102-6B.json