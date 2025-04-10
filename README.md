<h1 align="center">📊 FINACIAL DATA WAREHOUSE</h1>

# Chương 1: THIẾT KẾ DATA WAREHOUSE
## 1.1 Tìm hiểu nguồn dữ liệu
&nbsp;&nbsp;&nbsp;&nbsp;Nguồn dữ liệu được lấy từ các API do các tổ chức chuyên cung cấp dữ liệu cho thị trường chứng khoán, bao gồm các API sau:

### a. Sec-api
&nbsp;&nbsp;&nbsp;&nbsp; - Source: [sec-api.io – List Companies by Exchange](https://sec-api.io/docs/mapping-api/list-companies-by-exchange). </br>
&nbsp;&nbsp;&nbsp;&nbsp; - API này giúp truy xuất danh sách các công ty đang niêm yết trên các sàn chứng khoán như:
  **NYSE, NASDAQ, NYSEMKT, NYSEARCA, OTC, BATS, INDEX.** <br>
&nbsp;&nbsp;&nbsp;&nbsp; - Dữ liệu từ API trả về sẽ bao gồm các thuộc tính sau: 
  
| **Attribute**        | **Description** |
|----------------------|-----------------|
| `name`               | Tên công ty đã niêm yết trên sàn chứng khoán |
| `ticker`             | Ký hiệu trên sàn giao dịch chứng khoán (mã giao dịch cổ phiếu của công ty)  <br>→ Dùng để tra cứu và xác định giá cổ phiếu |
| `cik` <br> `(central index key)` | Mã định danh duy nhất cho mỗi công ty đã đăng ký với SEC (U.S Securities and Exchange Commission) <br>→ Tra cứu thông tin chi tiết của công ty trong các báo cáo của SEC |
| `cusip`              | Mã định danh duy nhất để nhận diện chứng khoán ở Mỹ (bao gồm cổ phiếu và trái phiếu) <br>→ Dùng để theo dõi chứng khoán, phân tích đầu tư và quản lý rủi ro |
| `exchange`           | Sàn chứng khoán nơi cổ phiếu của công ty được niêm yết |
| `isDelisted`         | Giá trị Boolean. Cho biết cổ phiếu đã bị hủy niêm yết hay chưa |
| `category`           | Hạng mục cổ phiếu |
| `sector`             | Ngành kinh tế mà công ty hoạt động |
| `industry`           | Ngành cụ thể của công ty |
| `sic` <br> `(Standard Industry Classification)` | Mã ngành nghề theo hệ thống phân loại SIC của chính phủ Mỹ |
| `sicSector`          | Ngành rộng theo mã SIC |
| `sicIndustry`        | Ngành cụ thể theo mã SIC |
| `famasection`        | Ngành theo mô hình Fama-French, phân chia theo yếu tố rủi ro và lợi suất (giá trị, tăng trưởng, quy mô,...) |
| `famaIndustry`       | Ngành cụ thể trong hệ thống phân loại của Fama-French |
| `currency`           | Đơn vị tiền tệ cổ phiếu được giao dịch (VD: USD, EUR) |
| `location`           | Địa chỉ hoặc khu vực hoạt động chính của công ty |
| `id`                 | Định danh công ty |


### b. Alpha Vantage
**API for market status*  
&nbsp;&nbsp;&nbsp;&nbsp;- Source: [alphavantage.co - Market Status](https://www.alphavantage.co/documentation/#market-status).  </br>
&nbsp;&nbsp;&nbsp;&nbsp;- API này cũng cấp thông tin về các thị trường chứng khoáng trên toàn thế giới. </br>
&nbsp;&nbsp;&nbsp;&nbsp;- Dữ liệu sau khi thu thập sẽ bao gồm các thuộc tính sau: </br>

| Attribute           | Description                                         |
|---------------------|-----------------------------------------------------|
| `market_type`       | Loại thị trường                                     |
| `region`            | Khu vực thị trường                                  |
| `primary_exchanges` | Sàn giao dịch chính                                 |
| `local_open`        | Thời gian mở cửa địa phương                         |
| `local_close`       | Thời gian đóng cửa địa phương                       |
| `current_status`    | Tình trạng hiện tại của thị trường                  |

**API for news sentimets* </br>
&nbsp;&nbsp;&nbsp;&nbsp;- Source: [alphavantage.co - News Sentiment](https://www.alphavantage.co/documentation/#news-sentiment).  </br>
&nbsp;&nbsp;&nbsp;&nbsp;- API Alpha Vantage cung cấp thông tin về sentiment của các tin tức và cảm xúc thị trường liên quan đến cổ phiếu.</br>

| Attribute                  | Description                                      |
|----------------------------|--------------------------------------------------|
| `title`                    | Tiêu đề bài viết                                 |
| `url`                      | Đường dẫn bài viết                               |
| `time_published`           | Thời gian xuất bản                               |
| `authors`                  | Tác giả                                          |
| `summary`                  | Tóm tắt bài viết                                 |
| `source`                   | Nguồn tin                                        |
| `source_domain`            | Tên miền của nguồn tin                           |
| `topics`                   | Danh sách chủ đề liên quan                       |
| `relevance_score`          | Điểm độ liên quan của bài viết                   |
| `overall_sentiment_score`  | Điểm cảm xúc tổng thể                            |
| `overall_sentiment_label`  | Nhãn cảm xúc tổng thể                            |
| `ticker_sentiment`         | Cảm xúc của cổ phiếu                             |
| `ticker`                   | Mã cổ phiếu                                      |
| `ticker_sentiment_score`   | Điểm cảm xúc của cổ phiếu                        |
| `ticker_sentiment_label`   | Nhãn cảm xúc của cổ phiếu                        |

### c. Polygon
## 1.2 Phân tích các bussiness process
## 1.3 Thiết kế data warehouse
# Chương 2: 
