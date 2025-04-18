-- Drop bảng trước nếu có
DROP TABLE IF EXISTS fact_company_sentiment;
DROP TABLE IF EXISTS fact_news_topic;
DROP TABLE IF EXISTS fact_stock_price;
DROP TABLE IF EXISTS dim_news;
-- DROP TABLE IF EXISTS dim_companies;
-- DROP TABLE IF EXISTS dim_date;

-- dim_date table
CREATE TABLE IF NOT EXISTS dim_date (
    day_key INT PRIMARY KEY,
    full_date DATE NOT NULL,
    day INT NOT NULL,
    month INT NOT NULL,
    year INT NOT NULL,
    quarter INT NOT NULL,
    week_of_year INT NOT NULL,
    day_of_week INT NOT NULL,
    day_name VARCHAR(20) NOT NULL
);

-- dim_companies table (SCD 2)
CREATE TABLE IF NOT EXISTS dim_companies (
    company_key BIGINT IDENTITY(1,1) PRIMARY KEY,
    company_id VARCHAR(255) NOT NULL, -- business key
    company_name VARCHAR(255) NOT NULL,
    company_ticker VARCHAR(10) NOT NULL,
    company_is_delisted BOOLEAN NOT NULL,
    company_category VARCHAR(255),
    company_currency VARCHAR(10) NOT NULL,
    company_location VARCHAR(255),
    company_exchange_name VARCHAR(100) NOT NULL,
    company_region_name VARCHAR(50) NOT NULL,
    company_industry_name VARCHAR(255),
    company_sic_industry VARCHAR(255),
    company_sic_sector VARCHAR(255),

    effective_date TIMESTAMP DEFAULT CURRENT_DATE NOT NULL,
    end_date TIMESTAMP DEFAULT NULL,
    is_current BOOLEAN DEFAULT TRUE
);

-- dim_news table (SCD 1)
CREATE TABLE IF NOT EXISTS dim_news (
    news_key BIGINT IDENTITY(1,1) PRIMARY KEY,
    news_id VARCHAR(255) NOT NULL UNIQUE, -- business key
    news_title VARCHAR(65535) NOT NULL,
    news_url VARCHAR(65535) NOT NULL,
    news_time_published TIMESTAMP NOT NULL,
    news_authors VARCHAR(255),
    news_summary VARCHAR(65535),
    news_source VARCHAR(65535),
    news_overall_sentiment_score DOUBLE PRECISION NOT NULL,
    news_overall_sentiment_label VARCHAR(255) NOT NULL,
    update_at TIMESTAMP DEFAULT CURRENT_DATE NOT NULL
);

-- fact_stock_price
CREATE TABLE IF NOT EXISTS fact_stock_price (
    company_key BIGINT NOT NULL,
    day_key INT NOT NULL,
    open_price DECIMAL(10, 2) NOT NULL,
    high_price DECIMAL(10, 2) NOT NULL,
    low_price  DECIMAL(10, 2) NOT NULL,
    close_price DECIMAL(10, 2) NOT NULL,
    volume INT NOT NULL,
    vwap DECIMAL(12, 6) NOT NULL,
    num_transaction INT NOT NULL,
    is_otc BOOLEAN DEFAULT false,
    PRIMARY KEY (company_key, day_key),
    FOREIGN KEY (company_key) REFERENCES dim_companies(company_key),
    FOREIGN KEY (day_key) REFERENCES dim_date(day_key)
);

-- fact_news_topic
CREATE TABLE IF NOT EXISTS fact_news_topic (
    news_key BIGINT NOT NULL,
    day_key INT NOT NULL,
    topic_relevance_score DOUBLE PRECISION NOT NULL,
    topic_name VARCHAR(100) NOT NULL,
    PRIMARY KEY (news_key, day_key),
    FOREIGN KEY (news_key) REFERENCES dim_news(news_key),
    FOREIGN KEY (day_key) REFERENCES dim_date(day_key)
);

-- fact_company_sentiment
CREATE TABLE IF NOT EXISTS fact_company_sentiment (
    company_key BIGINT NOT NULL,
    day_key INT NOT NULL,
    news_key BIGINT NOT NULL,
    sentiment_score DOUBLE PRECISION NOT NULL,
    sentiment_label VARCHAR(50) NOT NULL,
    relevance_score DOUBLE PRECISION NOT NULL,
    PRIMARY KEY (company_key, day_key, news_key),
    FOREIGN KEY (company_key) REFERENCES dim_companies(company_key),
    FOREIGN KEY (day_key) REFERENCES dim_date(day_key),
    FOREIGN KEY (news_key) REFERENCES dim_news(news_key)
);
