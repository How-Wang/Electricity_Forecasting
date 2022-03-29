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
    n_predictions= 16
    print(args)
    df_training = pd.read_csv(args.training) 
    df_training = pd.DataFrame(df_training)
    df_training['date']= pd.to_datetime(df_training['date'])

    prophet_data = df_training[:-n_predictions].rename(columns={'peak_supply': 'y', 'date': 'ds'})
    model_step_1 = Prophet(daily_seasonality=False, 
                            yearly_seasonality=True, 
                            weekly_seasonality=True,
                            changepoint_range=0.55,
                            seasonality_mode='additive')
    for regressor in ['is_holiday', 'month', 'year', 'day']:
        model_step_1.add_regressor(regressor)
    model_step_1.fit(prophet_data)
    df_future = df_training[-n_predictions:].rename(columns={'peak_supply': 'y', 'date': 'ds'})
    df_forecast_step_1 = model_step_1.predict(df_future)
    df_forecast_step_1 = df_forecast_step_1[['ds', 'yhat']]
    df_forecast_step_1.columns = ['date', 'peak_supply']

    prophet_data = df_training[:-n_predictions].rename(columns={'date': 'ds', 'prcnt_op_reserve': 'y'})
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
    df_future = df_training[-n_predictions:].rename(columns={'peak_supply': 'y', 'date': 'ds'})
    df_future['peak_supply'] = df_forecast_step_1['peak_supply'].values
    df_forecast_step_2 = model_step_2.predict(df_future)
    df_forecast_step_2 = df_forecast_step_2[['ds', 'yhat']]
    df_forecast_step_2.columns = ['date', 'prcnt_op_reserve']

    df_result = df_forecast_step_1.merge(df_forecast_step_2)
    op_reserve = [float] * len(df_result['peak_supply'])
    for i, item in enumerate (op_reserve):
        op_reserve[i] = df_result.loc[:,('peak_supply')][i] * df_result.loc[:,('prcnt_op_reserve')][i] / 100
    df_result['op_reserve'] = op_reserve

    df_result = df_result.loc[:, ['date', 'op_reserve']]

    new_date = [str] * len(df_result['date'])
    for i, date in enumerate(df_result['date']):
        new_date[i] = str(date).replace('-', '')[:8]
    df_result['date'] = new_date

    df_result.columns = ['date', 'operating_reserve(MW)']

    df_result.to_csv(args.output, index=0)
