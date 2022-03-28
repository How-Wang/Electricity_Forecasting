# Taiwan Electricity Forecasting
## 總覽
>We will implement an algorithm to predict the operating reserve (備轉容量) of electrical power.
Given a time series electricity data to predict the value of the operating reserve value of each day during 2022/03/30 ~ 2022/04/13.

## 資料呈現與分析
### 訓練資料與觀察
根據[**台灣電力公司_本年度每日尖峰備轉容量率.csv**](https://data.gov.tw/dataset/25850)、[**台灣電力公司_過去電力供需資訊2021.csv**](https://data.gov.tw/dataset/19995)
我們先針對三種數值進行視覺化
- 橙色 尖峰負載 peak supply
- 綠色 備轉容量 operation reserve
- 藍色 備轉容量率 operation reserve rate

![](https://i.imgur.com/UT71PJG.png)
![](https://i.imgur.com/xga6xI9.png)

而我們又可以知道
- **備轉容量 = 尖峰負載 * 備轉容量率**
- 根據觀察可得，**橘色的尖峰負載 peak supply** 呈現明顯的趨勢，而 **藍色的備轉容量率 operation reserve ratio** 在2020年初的階段以來，如果排除掉 outlier，最低的備轉容量都能維持在10%以上
所以本次預測，會先預測

1. 尖峰負載 peak supply
2. 備轉容量率 operation reserve ratio

在利用兩者相乘得出我們所求的 備轉容量率 operation reserve ratio
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
如果再進一步判斷 **季節性 seasonality** 與 **備轉容量率 operation reserve ratio**，就能進一步確認上續推斷，除了 month 之外，其他的 feature 並沒有與 operation reserve ratio 有什麼相關性，也包含我們可能認為會有相關的 holiday

- 與 operation reserve ratio 相比
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
在 training 資料內，我們使用2017年至2022年的一維資料，包含 **尖峰負載 peak supply**、**備轉容量率 operation reserve rate**
## 使用模型
- FB-prophet
我們在經過測試之後，決定使用 facebook 所提供的模型 [prophet](https://github.com/facebook/prophet)
>Forecasting is a data science task that is central to many activities within an organization.
For instance, organizations across all sectors of industry must engage in capacity planning
to efficiently allocate scarce resources and goal setting in order to measure performance
relative to a baseline. 
詳細內容可以再參照 [(Sean J. Taylor&Benjamin Letham,2017)](https://peerj.com/preprints/3190/#)

我們共使用兩次 prophet 模型兩次，分別為
1. 尖峰負載 peak supply
![](https://i.imgur.com/TFQhb5q.png)
`RMSE = 595.9370547869777`

2. 備轉容量率 operation reserve ratio
![](https://i.imgur.com/AbczJxY.png)
`RMSE = 1.761063198150491`

## 初步測試結果
根據
1. **尖峰負載 peak supply** 與 **備轉容量率 operation reserve ratio** 的兩種預測
2. 備轉容量 = 尖峰負載 * 備轉容量率

可以得知，我們的預測結果應為兩者的預測**乘積**

![](https://i.imgur.com/nyihzqe.png)
`RMSE = 523.339138543489`

## 結論
在此次作業中，我們可以觀察出關於**備載容量率**，並沒有明顯的可預測性，因為我們本次需要預測的並不是有明顯季節性的尖峰負載 peak supply，而是台電可以動態調整的電樣備載率；但我們的模型能夠很好的掌握**平均值**
- 所以我們的策略的是先掌握 有季節性的**尖峰負載 peak supply**
- 再試著預測 **備轉容量率 operation reserve ratio**，進而得到備轉容量

但因為 備轉容量率 operation reserve ratio 也較難預測，所以導致相乘後的結果也較不為準確