# echo "04/27 Q66b-6B 1 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 precompute_truecards1d.py ../input_configs/imdb_precompute_config_Q66b-6B.json
# echo "04/27 Q66b-6B 2 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 execute_trainingset1d.py ../input_configs/imdb_trainingset_config_Q66b-6B.json
# echo "04/27 Q66b-6B 3 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 truecard_main1d.py ../input_configs/imdb_true-card_config_Q66b-6B.json
# echo "04/27 Q66b-6B 4-------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 base_main1d.py ../input_configs/imdb_no-retrain_no-cache_config_Q66b-6B.json
# echo "05/05 Q66b-6B 5 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 baseline1d.py ../input_configs/imdb_baseline_config_Q66b-6B_rt1.json
# echo "05/05 Q66b-6B 6 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 baseline1d.py ../input_configs/imdb_baseline_config_Q66b-6B_rt3.json
# echo "05/05 Q66b-6B 7 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 baseline1d.py ../input_configs/imdb_baseline_config_Q66b-6B_rt6.json



# echo "04/27 Q68-6B 1 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 precompute_truecards1d.py ../input_configs/imdb_precompute_config_Q68-6B.json
# echo "04/27 Q68-6B 2 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 execute_trainingset1d.py ../input_configs/imdb_trainingset_config_Q68-6B.json
# echo "04/27 Q68-6B 3 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 truecard_main1d.py ../input_configs/imdb_true-card_config_Q68-6B.json
# echo "04/27 Q68-6B 4-------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 base_main1d.py ../input_configs/imdb_no-retrain_no-cache_config_Q68-6B.json
# echo "05/05 Q68-6B 5 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 baseline1d.py ../input_configs/imdb_baseline_config_Q68-6B_rt1.json
# echo "05/05 Q68-6B 6 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 baseline1d.py ../input_configs/imdb_baseline_config_Q68-6B_rt3.json
# echo "05/05 Q68-6B 7 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 baseline1d.py ../input_configs/imdb_baseline_config_Q68-6B_rt6.json



# echo "04/27 Q70-6B 2 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 execute_trainingset1d.py ../input_configs/imdb_trainingset_config_Q70-6B.json
# echo "04/27 Q70-6B 1 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 precompute_truecards1d.py ../input_configs/imdb_precompute_config_Q70-6B.json
# echo "04/27 Q70-6B 3 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 truecard_main1d.py ../input_configs/imdb_true-card_config_Q70-6B.json
# echo "04/27 Q70-6B 4-------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 base_main1d.py ../input_configs/imdb_no-retrain_no-cache_config_Q70-6B.json
# echo "05/05 Q70-6B 5 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 baseline1d.py ../input_configs/imdb_baseline_config_Q70-6B_rt1.json
# echo "05/05 Q70-6B 6 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 baseline1d.py ../input_configs/imdb_baseline_config_Q70-6B_rt3.json
# echo "05/05 Q70-6B 7 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 baseline1d.py ../input_configs/imdb_baseline_config_Q70-6B_rt6.json



# echo "05/06 Q68-6B 8 ---------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 twotier_main1d.py ../input_configs/imdb_twotier_config_Q68-6B.json
# echo "05/06 Q68-6B 9 ---------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 twotier_main1d.py ../input_configs/imdb_twotier_config_Q68-6B_correctjoin2.json

# echo "05/06 Q66b-6B 8 ---------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 twotier_main1d.py ../input_configs/imdb_twotier_config_Q66b-6B.json




# echo "05/06 Q66b-6B 9 ---------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 twotier_main1d.py ../input_configs/imdb_twotier_config_Q66b-6B_correctjoin2.json

# echo "05/06 Q70-6B 8 ---------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 twotier_main1d.py ../input_configs/imdb_twotier_config_Q70-6B.json
# echo "05/06 Q70-6B 9 ---------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 twotier_main1d.py ../input_configs/imdb_twotier_config_Q70-6B_correctjoin2.json


# echo "04/27 Q36-6B 1 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 precompute_truecards1d.py ../input_configs/imdb_precompute_config_Q36-6B.json
# echo "04/27 Q36-6B 2 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 execute_trainingset1d.py ../input_configs/imdb_trainingset_config_Q36-6B.json
# echo "04/27 Q36-6B 3 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 truecard_main1d.py ../input_configs/imdb_true-card_config_Q36-6B.json
# echo "04/27 Q36-6B 4-------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 base_main1d.py ../input_configs/imdb_no-retrain_no-cache_config_Q36-6B.json
# echo "05/05 Q36-6B 5 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 baseline1d.py ../input_configs/imdb_baseline_config_Q36-6B_rt1.json
# echo "05/05 Q36-6B 6 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 baseline1d.py ../input_configs/imdb_baseline_config_Q36-6B_rt3.json
# echo "05/05 Q36-6B 7 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 baseline1d.py ../input_configs/imdb_baseline_config_Q36-6B_rt6.json



# echo "04/27 Q44-6B 1 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 precompute_truecards1d.py ../input_configs/imdb_precompute_config_Q44-6B.json
# echo "04/27 Q44-6B 2 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 execute_trainingset1d.py ../input_configs/imdb_trainingset_config_Q44-6B.json
# echo "04/27 Q44-6B 3 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 truecard_main1d.py ../input_configs/imdb_true-card_config_Q44-6B.json
# echo "04/27 Q44-6B 4-------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 base_main1d.py ../input_configs/imdb_no-retrain_no-cache_config_Q44-6B.json
# echo "05/05 Q44-6B 5 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 baseline1d.py ../input_configs/imdb_baseline_config_Q44-6B_rt1.json
# echo "05/05 Q44-6B 6 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 baseline1d.py ../input_configs/imdb_baseline_config_Q44-6B_rt3.json
# echo "05/05 Q44-6B 7 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 baseline1d.py ../input_configs/imdb_baseline_config_Q44-6B_rt6.json



# echo "05/06 Q36-6B 8 ---------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 twotier_main1d.py ../input_configs/imdb_twotier_config_Q36-6B.json
# echo "05/06 Q36-6B 9 ---------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 twotier_main1d.py ../input_configs/imdb_twotier_config_Q36-6B_correctjoin2.json

# echo "05/06 Q44-6B 8 ---------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 twotier_main1d.py ../input_configs/imdb_twotier_config_Q44-6B.json
# echo "05/06 Q44-6B 9 ---------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 twotier_main1d.py ../input_configs/imdb_twotier_config_Q44-6B_correctjoin2.json

# echo "05/08 Q36-6B 9 ---------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 leo_main1d.py ../input_configs/imdb_leo_config_Q36-6B.json
# echo "05/08 Q36-6B 10 ---------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 main1d.py ../input_configs/imdb_config_Q36-6B.json

# echo "05/09 1 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 pg_main1d.py ../input_configs/imdb_pg_config_Q36-6B.json
# echo "05/09 2 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 pg_main1d.py ../input_configs/imdb_pg_config_Q44-6B.json
# echo "05/09 3 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 pg_main1d.py ../input_configs/imdb_pg_config_Q66b-6B.json
# echo "05/09 4 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 pg_main1d.py ../input_configs/imdb_pg_config_Q68-6B.json
# echo "05/09 5 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 pg_main1d.py ../input_configs/imdb_pg_config_Q70-6B.json




# echo "05/24 Q68-6B-change 1 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 precompute_truecards1d.py ../input_configs/imdb_precompute_config_Q68-6B-change.json
# echo "05/24 Q68-6B-change 2 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 execute_trainingset1d.py ../input_configs/imdb_trainingset_config_Q68-6B-change.json
# echo "05/24 Q68-6B-change 3 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 truecard_main1d.py ../input_configs/imdb_true-card_config_Q68-6B-change.json
# echo "05/24 Q68-6B-change 4-------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 base_main1d.py ../input_configs/imdb_no-retrain_no-cache_config_Q68-6B-change.json
# echo "05/24 Q68-6B-change 5 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 baseline1d.py ../input_configs/imdb_baseline_config_Q68-6B-change_rt1.json
# echo "05/24 Q68-6B-change 6 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 baseline1d.py ../input_configs/imdb_baseline_config_Q68-6B-change_rt3.json
# echo "05/24 Q68-6B-change 7 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 baseline1d.py ../input_configs/imdb_baseline_config_Q68-6B-change_rt6.json



# echo "05/24 Q66b-6B-change 1 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 precompute_truecards1d.py ../input_configs/imdb_precompute_config_Q66b-6B-change.json
# echo "05/24 Q66b-6B-change 2 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 execute_trainingset1d.py ../input_configs/imdb_trainingset_config_Q66b-6B-change.json
# echo "05/24 Q66b-6B-change 3 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 truecard_main1d.py ../input_configs/imdb_true-card_config_Q66b-6B-change.json
# echo "05/24 Q66b-6B-change 4-------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 base_main1d.py ../input_configs/imdb_no-retrain_no-cache_config_Q66b-6B-change.json
# echo "05/24 Q66b-6B-change 5 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 baseline1d.py ../input_configs/imdb_baseline_config_Q66b-6B-change_rt1.json
# echo "05/24 Q66b-6B-change 6 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 baseline1d.py ../input_configs/imdb_baseline_config_Q66b-6B-change_rt3.json
# echo "05/24 Q66b-6B-change 7 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 baseline1d.py ../input_configs/imdb_baseline_config_Q66b-6B-change_rt6.json



# echo "05/24 Q70-6B-change 1 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 precompute_truecards1d.py ../input_configs/imdb_precompute_config_Q70-6B-change.json
# echo "05/24 Q70-6B-change 2 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 execute_trainingset1d.py ../input_configs/imdb_trainingset_config_Q70-6B-change.json
# echo "05/24 Q70-6B-change 3 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 truecard_main1d.py ../input_configs/imdb_true-card_config_Q70-6B-change.json
# echo "05/24 Q70-6B-change 4-------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 base_main1d.py ../input_configs/imdb_no-retrain_no-cache_config_Q70-6B-change.json
# echo "05/24 Q70-6B-change 5 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 baseline1d.py ../input_configs/imdb_baseline_config_Q70-6B-change_rt1.json
# echo "05/24 Q70-6B-change 6 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 baseline1d.py ../input_configs/imdb_baseline_config_Q70-6B-change_rt3.json
# echo "05/24 Q70-6B-change 7 -------"
# dropdb -p 5555 watcherdb
# createdb -p 5555 -U ANONYMOUS watcherdb
# python3 baseline1d.py ../input_configs/imdb_baseline_config_Q70-6B-change_rt6.json



echo "05/24 Q68-6B-change 8 ---------"
dropdb -p 5555 watcherdb
createdb -p 5555 -U ANONYMOUS watcherdb
python3 twotier_main1d.py ../input_configs/imdb_twotier_config_Q68-6B-change.json
echo "05/24 Q68-6B-change 9 ---------"
dropdb -p 5555 watcherdb
createdb -p 5555 -U ANONYMOUS watcherdb
python3 twotier_main1d.py ../input_configs/imdb_twotier_config_Q68-6B-change_correctjoin2.json


echo "05/24 Q66b-6B-change 8 ---------"
dropdb -p 5555 watcherdb
createdb -p 5555 -U ANONYMOUS watcherdb
python3 twotier_main1d.py ../input_configs/imdb_twotier_config_Q66b-6B-change.json
echo "05/24 Q66b-6B-change 9 ---------"
dropdb -p 5555 watcherdb
createdb -p 5555 -U ANONYMOUS watcherdb
python3 twotier_main1d.py ../input_configs/imdb_twotier_config_Q66b-6B-change_correctjoin2.json


echo "05/24 Q70-6B-change 8 ---------"
dropdb -p 5555 watcherdb
createdb -p 5555 -U ANONYMOUS watcherdb
python3 twotier_main1d.py ../input_configs/imdb_twotier_config_Q70-6B-change.json
echo "05/24 Q70-6B-change 9 ---------"
dropdb -p 5555 watcherdb
createdb -p 5555 -U ANONYMOUS watcherdb
python3 twotier_main1d.py ../input_configs/imdb_twotier_config_Q70-6B-change_correctjoin2.json




echo "05/24 Q70-6B-change 5 -------"
dropdb -p 5555 watcherdb
createdb -p 5555 -U ANONYMOUS watcherdb
python3 baseline1d.py ../input_configs/imdb_baseline_config_Q70-6B-change_rt1.json