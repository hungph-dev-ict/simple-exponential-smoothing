import pandas as pd
import numpy as np
import datetime
import time
from datetime import timedelta
import json

price_df = pd.read_csv('data/DatafinitiElectronicsProductsPricingData.csv')

sort_by_id = price_df['id'].value_counts()
sort_by_id = pd.DataFrame({'id':sort_by_id.index}).merge(price_df, how='left')

most_record_id = sort_by_id['id'].iloc[0]
final_list = price_df[price_df['id'] == most_record_id][['id', 'dateUpdated', 'prices.amountMax']].values
time_now = datetime.datetime.now()
new_time = time_now
count_day = 0
for item in final_list:
    new_time = new_time + timedelta(days=1)
    item[1] = new_time.strftime('%Y-%m-%dT%H:%M:%S:%fZ')

final_df = pd.DataFrame(data=final_list, columns=['id', 'timestamp', 'demand'])
final_df.to_csv('foo.csv', index=False)

def est_algorithm(file_path=None, alpha=0.2, log_cli=True):
    start_time = time.time()
    df = pd.read_csv(file_path)
    all_record_list = df.values.tolist()
    absolute_deviation = 0
    for index, item in enumerate(all_record_list):
        if index == 0:
            item.append(item[2])
        else:
            previous_predict_value = all_record_list[index - 1][3]
            previous_actual_value = all_record_list[index - 1][2]
            est_recipe_value = previous_predict_value + alpha*(previous_actual_value - previous_predict_value)
            item.append(est_recipe_value)
            absolute_deviation += abs(item[2] - item[3])
    
    # Calculate MAD
    mean_absolute_deviation = absolute_deviation/len(all_record_list)
    end_time = time.time()
    if log_cli == True:
        print('-------------------------')
        print('MSE: ' + str(round(mean_absolute_deviation,4)))
        print('Calculate time: ' + str(round((end_time - start_time), 4)))
        print('-------------------------')
    result = {}
    result['mse_value'] = mean_absolute_deviation
    result['calculate_time'] = round((end_time - start_time), 4)
    
    return json.dumps(result)

def choose_best_alpha(file_path=None, frequency=0.2, criterions='mse_value'):
    alpha_list = np.arange(0.01, 1, frequency).tolist()
    min_mse_value = json.loads(est_algorithm(file_path=file_path, alpha=0.2, log_cli=False))['mse_value']    
    min_calculate_time = json.loads(est_algorithm(file_path=file_path, alpha=0.2, log_cli=False))['calculate_time']
    best_alpha = 0.2
    print('*********************')    
    for alpha in alpha_list:
        print('Process with alpha = ' + str(alpha))
        result = est_algorithm(file_path=file_path, alpha=alpha)
        mse_value = json.loads(result)['mse_value']
        calculate_time = json.loads(result)['calculate_time']
        if criterions == 'mse_value':        
            if mse_value < min_mse_value:
                min_mse_value = mse_value
                min_calculate_time = calculate_time
                best_alpha = alpha
        if criterions == 'calculate_time':
            if calculate_time < min_calculate_time:
                min_mse_value = mse_value
                min_calculate_time = calculate_time
                best_alpha = alpha
    
    print('Best alpha: ' + str(best_alpha) + ' with MSE value: ' + str(round(min_mse_value,4)) + ' and calculate time: ' + str(min_calculate_time) + 's')
    print('*********************')
    
    return alpha

choose_best_alpha('foo.csv', frequency=0.05, criterions='mse_value')