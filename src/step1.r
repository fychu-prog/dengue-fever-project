# 載入必要套件
library(tidyverse)
library(lubridate)

# 讀取 CSV 資料
# 方法1: 如果已下載到本地
# 查看目前工作目錄
getwd()

# 設定工作目錄到你的專案資料夾
setwd("E://folder_python//dengue_fever_project")

# 之後就可以直接用檔名或相對路徑
dengue <- read.csv("data//raw//Dengue_Daily.csv")

# 查看資料結構
str(dengue)
head(dengue)
summary(dengue)


# 轉換日期格式
dengue <- dengue %>%
  mutate(
    發病日期 = ymd(發病日),
    發病年 = year(ymd(發病日)),
    發病月 = month(ymd(發病日))
  )

# 1. 查看確定病例數的資料類型
class(dengue$確定病例數)

# 2. 查看前 20 筆資料
head(dengue$確定病例數, 20)

# 3. 查看統計摘要
summary(dengue$確定病例數)

# 4. 檢查有沒有 NA (缺失值)
sum(is.na(dengue$確定病例數))

# 5. 查看不重複的值有哪些
unique(dengue$確定病例數)

# 6. 計算總和
sum(dengue$確定病例數, na.rm = TRUE)


library(dplyr)
library(lubridate)
library(ggplot2)

# 資料清理
dengue_clean <- dengue %>%
  mutate(
    發病日期 = ymd(發病日),
    發病年 = year(ymd(發病日)),
    發病月 = month(ymd(發病日)),
    發病年月 = floor_date(ymd(發病日), "month")
  ) %>%
  filter(!is.na(發病日期)) # 移除日期錯誤的資料

# 查看清理後有多少筆
nrow(dengue_clean)

dengue_clean %>%
  filter(確定病例數 == 2)

# 步驟 2: 時間趨勢分析
# 1. 每年病例數 (正確方式: 直接計算列數)
yearly_cases <- dengue_clean %>%
  count(發病年, name = "病例數") %>%
  arrange(發病年)

print(yearly_cases)

# 2. 找出疫情最嚴重的年份
yearly_cases %>%
  arrange(desc(病例數)) %>%
  head(10)

# 3. 每月病例數 (看季節性)
monthly_cases <- dengue_clean %>%
  count(發病年月, name = "病例數") %>%
  arrange(發病年月)

print(head(monthly_cases, 20))

# 3.5 排名最多的年月
monthly_cases <- dengue_clean %>%
  count(發病年月, name = "病例數") %>%
  arrange(desc(病例數))

print(head(monthly_cases, 20))


# 4. 月份平均值 (季節性模式)
monthly_pattern <- dengue_clean %>%
  count(發病月, name = "病例數") %>%
  mutate(平均病例數 = 病例數 / length(unique(dengue_clean$發病年)))

print(monthly_pattern)



# 步驟 3: 地區分析
# 1. 各縣市病例數
county_cases <- dengue_clean %>%
  count(居住縣市, name = "病例數") %>%
  mutate(佔比 = 病例數 / sum(病例數) * 100) %>%
  arrange(desc(病例數))

print(county_cases)

# 2. 台南、高雄逐年比較 (你的研究重點)
south_yearly <- dengue_clean %>%
  filter(居住縣市 %in% c("台南市", "高雄市")) %>%
  count(居住縣市, 發病年, name = "病例數") %>%
  arrange(居住縣市, 發病年)

print(south_yearly)

south_yearly_wide <- dengue_clean %>%
  filter(居住縣市 %in% c("台南市", "高雄市")) %>%
  count(發病年, 居住縣市, name = "病例數") %>%
  pivot_wider(
    names_from = 居住縣市,
    values_from = 病例數,
    values_fill = 0
  ) %>%
  arrange(發病年)

print(south_yearly_wide, n = 28)

# 3. 台南、高雄月度資料 (可用於 LASSO 模型)
south_monthly <- dengue_clean %>%
  filter(居住縣市 %in% c("台南市", "高雄市")) %>%
  count(居住縣市, 發病年, 發病月, name = "病例數") %>%
  arrange(居住縣市, 發病年, 發病月)

print(head(south_monthly, 20))

# 4. 高雄各區 Top 10
kaohsiung_districts <- dengue_clean %>%
  filter(居住縣市 == "高雄市") %>%
  count(居住鄉鎮, name = "病例數") %>%
  arrange(desc(病例數)) %>%
  head(10)

print(kaohsiung_districts)


# 步驟 4: 本土 vs 境外移入
# 1. 整體比例
source_summary <- dengue_clean %>%
  count(是否境外移入, name = "病例數") %>%
  mutate(百分比 = 病例數 / sum(病例數) * 100)

print(source_summary)

# 2. 逐年趨勢
source_yearly <- dengue_clean %>%
  count(發病年, 是否境外移入, name = "病例數") %>%
  arrange(發病年, 是否境外移入)

print(source_yearly)

# 3. 台南高雄的本土案例 (用於你的模型)
south_local <- dengue_clean %>%
  filter(
    居住縣市 %in% c("臺南市", "高雄市"),
    是否境外移入 == "否"
  ) %>%
  count(居住縣市, 發病年, 發病月, name = "本土病例數")

print(head(south_local, 20))
