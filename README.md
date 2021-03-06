# Taiwan Electricity Forecasting
## 總覽
>We will implement an algorithm to predict the operating reserve (備轉容量) of electrical power.
Given a time series electricity data to predict the value of the operating reserve value of each day during 2022/03/30 ~ 2022/04/13.

## 資料呈現與分析
### 訓練資料與觀察
根據[**台灣電力公司_本年度每日尖峰備轉容量率.csv**](https://data.gov.tw/dataset/25850)、[**台灣電力公司_過去電力供需資訊2021.csv**](https://data.gov.tw/dataset/19995)

我們先針對三種數值進行視覺化
- 橙色 尖峰負載 peak supply
- 綠色 備轉容量 operating reserve
- 藍色 備轉容量率 percent operating reserve

![](https://i.imgur.com/UT71PJG.png)
![](https://i.imgur.com/xga6xI9.png)

而我們又可以知道
- **備轉容量 = 尖峰負載 * 備轉容量率**
- 根據觀察可得，**橘色的尖峰負載 peak supply** 呈現明顯的趨勢，而 **藍色的備轉容量率 percent operating reserve** 在2020年初的階段以來，如果排除掉 outlier，最低的備轉容量都能維持在10%以上
所以本次預測，會先預測

1. 尖峰負載 peak supply
2. 備轉容量率 percent operating reserve

在利用兩者相乘得出我們所求的 備轉容量率 percent operating reserve

### 相關係數
根據下方常見的5種相關係數 分別為
Pearson's r、Maximal information Coefficient、Distance Correlation、Spearman's Rho、Kendall Tau
1. 很顯然 **備轉率** 與 **備轉容量率** 很相關
2. **month** 與 **備轉容量率** 也有較大的相關性
3. 但其他特徵(year、is_holiday)就只有在**非線性**的角度觀察(Maximal information、Distance)時，才有些許較高的相關性  
![](https://i.imgur.com/ujFrTbT.png)
![](https://i.imgur.com/UDUJQTF.png)
![](https://i.imgur.com/rOFXhIz.png)
![](https://i.imgur.com/9GbTCvf.png)
![](https://i.imgur.com/jA05jJC.png)

### 季節性判斷
如果再進一步判斷 **季節性 seasonality** 與 **備轉容量率 percent operating reserve**，就能進一步確認上續推斷，除了 month 之外，其他的 features 並沒有與 percent operating reserve 有什麼相關性，也包含我們可能認為會有相關的 holiday

- 與 percent operating reserve 相比
    - day

![](https://i.imgur.com/7u11Mmq.png)
    - month  
![](https://i.imgur.com/LbInxae.png)
    - day_of_week  
![](https://i.imgur.com/RU5TRAQ.png)
    - is_holiday  
![](https://i.imgur.com/D7LeyIM.png)
  
- peak 與 peak ratio 相比  
![](https://i.imgur.com/MWrqFyh.png)
- is_holiday 與 peak  
![](https://i.imgur.com/ckSmI21.png)

## 資料前處理
在 training 資料內，我們使用2017年至2022年的一維資料，包含 **尖峰負載 peak supply**、**備轉容量率 operating reserve ratio**
## 使用模型
### 1. XGBoost
>XGBoost is an optimized distributed gradient boosting library designed to be highly efficient, flexible and portable. It implements machine learning algorithms under the Gradient Boosting framework.

1. 首先在現有的資料內，我們選取當日的 `日期`  
![](https://i.imgur.com/vujDXQS.png)
當作測試  

2. 我們也測試 feature 加上了`前幾天`的 
    - `備轉率`
    - `備轉量`
    - `備轉量` + `備轉率`
 
我們發現當feature 選擇`備轉量`時，會有最好的效果  
3. 下一步，我們開始測試天數的效果，以下為效果呈現  
![](https://i.imgur.com/Tv5ZWvP.png)
根據上圖，發現 rmse 的範圍會落在 436.64~1059，range 想當大  
且平均與中位數大約都落於 650 左右，風險不小  
下方為預測效果最好的天數與 features 組合 XGBoost  
天數 : 64   
![](https://i.imgur.com/uuhgXVc.png)



### 2. Arima
>In statistics and econometrics, and in particular in time series analysis, an autoregressive integrated moving average (ARIMA) model is a generalization of an autoregressive moving average (ARMA) model. Both of these models are fitted to time series data either to better understand the data or to predict future points in the series (forecasting). 

Arima 的特色與限制就是只能帶入一維的 time series 變數，沒辦法再加上日期或是其他 features。  
1. 我們先調整帶入的歷史日期，去測試效果  
![](https://i.imgur.com/q2pKYCX.png)
2. 接著改變帶入原始資料的方式，改帶入**相差值**，預測結果  
![](https://i.imgur.com/D9cqxGq.png)

### 3. FB-prophet
我們在經過測試之後，決定使用 facebook 所提供的模型 [prophet](https://github.com/facebook/prophet)  
>Forecasting is a common data science task that helps organizations with capacity planning, goal setting, and anomaly detection. Despite its importance, there are serious challenges associated with producing reliable and high quality forecasts — especially when there are a variety of time series and analysts with expertise in time series modeling are relatively rare. To address these challenges, we describe a practical approach to forecasting “at scale” that combines configurable models with analyst-in-the-loop performance analysis. We propose a modular regression model with interpretable parameters that can be intuitively adjusted by analysts with domain knowledge about the time series. We describe performance analyses to compare and evaluate forecasting procedures, and automatically flag forecasts for manual review and adjustment. Tools that help analysts to use their expertise most effectively enable reliable, practical forecasting of business time series. 
詳細內容可以再參照 [(Sean J. Taylor&Benjamin Letham,2017)](https://peerj.com/preprints/3190/#)

此模型依舊為 Time series 模型，但與 ARIMA 不同的是，我們可以在此模型上，多加上其他 features 的 time series data 當 regressor。

- e.g. 當天是否為 holiday、星期幾、月份、年分
- e.g. 分多個步驟進行 time series 建立。先建立模型 A、再利用模型 A 的預測結果，當成模型 B 的 regressor，再預測模型 B。

我們共使用兩次 prophet 模型兩次，分別為  
1. 尖峰供電 peak supply  
![](https://i.imgur.com/TFQhb5q.png)  
`RMSE = 595.9370547869777`  
  
2. 備轉容量率 operation reserve ratio  
![](https://i.imgur.com/AbczJxY.png)  
`RMSE = 1.761063198150491`  


## 初步測試結果
根據
1. **尖峰負載 peak supply** 與 **備轉容量率 percent operating reserve** 的兩種預測
2. 備轉容量 = 尖峰負載 * 備轉容量率

可以得知，我們的預測結果應為兩者的預測**乘積**  

![](https://i.imgur.com/nyihzqe.png)  
`RMSE = 523.339138543489`  

## 結論

在此次作業中，我們可以觀察出關於**備載容量率**，並沒有明顯的可預測性，因為我們本次需要預測的並不是有明顯季節性的尖峰負載 peak supply，而是台電可以動態調整的電樣備載率；但我們的模型能夠很好的掌握**平均值**
- 所以我們的策略的是先掌握 有季節性的**尖峰負載 peak supply**
- 再試著預測 **備轉容量率 percent operating reserve**，進而得到備轉容量

但因為備轉容量率 percent operating reserve 也較難預測，所以導致相乘後的結果也較不為準確，不過相比直接預測備轉容量，其準確度還是可靠許多。
