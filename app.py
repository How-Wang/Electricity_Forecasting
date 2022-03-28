if __name__ == '__main__':
    # You should not modify this part, but additional arguments are allowed.
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--training',
                       default='training_data.csv',
                       help='input training data file name')

    parser.add_argument('--output',
                        default='submission.csv',
                        help='output file name')
    args = parser.parse_args()
    
    # The following part is an example.
    # You can modify it at will.
    import pandas as pd
    from prophet import Prophet
    
    df_training = pd.read_csv(args.training)
    prophet_data = df_training.rename(columns={'date': 'ds', 'peak_supply': 'y'})
    model_step_1 = Prophet(daily_seasonality=False, 
                            yearly_seasonality=True, 
                            weekly_seasonality=True,
                            changepoint_range=0.55,
                            seasonality_mode='additive')
    for regressor in ['is_holiday', 'month', 'year', 'day']:
        model_step_1.add_regressor(regressor)
    model_step_1.fit(prophet_data)
    df_future = model_step_1.make_future_dataframe(periods=15)
    print(df_future)
    df_forecast_step_1 = model_step_1.predict(df_future)
    df_forecast_step_1 = df_forecast_step_1[['ds', 'yhat']]
    df_forecast_step_1.columns = ['date', 'peak_load']

    prophet_data = df_training.rename(columns={'date': 'ds', 'op_reserve_ratio': 'y'})
    model_step_2 = Prophet(daily_seasonality=False, 
                            yearly_seasonality=True, 
                            weekly_seasonality=False, 
                            seasonality_mode='additive',
                            changepoint_range=0.9,
                            changepoint_prior_scale=100,
                            seasonality_prior_scale=100)
    for regressor in ['peak_supply', 'is_holiday', 'month', 'year', 'day']:
        model_step_2.add_regressor(regressor)
    model_step_2.fit(prophet_data)
    df_future = model_step_2.make_future_dataframe(periods=15)
    df_future['peak_supply'] = df_forecast_step_1['yhat'].values
    df_forecast_step_2 = model_step_1.predict(df_future)
    df_forecast_step_2 = df_forecast_step_2[['ds', 'yhat']]
    df_forecast_step_2.columns = ['date', 'op_reserve_ratio']

    df_result = df_forecast_step_1.merge(df_forecast_step_2)
    df_result['op_reserve'] = ''
    for i, item in enumerate (df_result['op_reserve']):
        df_result['op_reserve'][i] = df_result['peak_supply'] * df_result['op_reserve_ratio'] / 100

    df_result.to_csv(args.output, index=0)
