-- 创建 profiles 表
CREATE TABLE profiles (
    user_id UUID PRIMARY KEY,
    nickname TEXT,
    avatar_url TEXT,
    locale TEXT,
    plan TEXT,
    plan_renews_at TIMESTAMP
);

-- 创建 sources 表
CREATE TABLE sources (
    id SERIAL PRIMARY KEY,
    name TEXT,
    url TEXT,
    type TEXT,
    lang TEXT,
    enabled BOOLEAN
);

-- 创建 articles 表
CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    source_id INT REFERENCES sources(id),
    url TEXT,
    title TEXT,
    author TEXT,
    published_at TIMESTAMP,
    lang TEXT,
    hash TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 创建 article_contents 表
CREATE TABLE article_contents (
    article_id INT REFERENCES articles(id),
    raw_html TEXT,
    text_content TEXT,
    summary TEXT,
    translated_summary TEXT,
    translated_lang TEXT,
    meta JSONB
);

-- 创建 user_prefs 表
CREATE TABLE user_prefs (
    user_id UUID REFERENCES profiles(user_id),
    source_id INT REFERENCES sources(id),
    keywords TEXT[],
    lang TEXT
);

-- 创建 usage_quotas 表
CREATE TABLE usage_quotas (
    user_id UUID REFERENCES profiles(user_id),
    day DATE,
    summarize_tokens INT,
    translate_chars INT
);

-- 创建 subscriptions 表
CREATE TABLE subscriptions (
    user_id UUID REFERENCES profiles(user_id),
    stripe_customer_id TEXT,
    stripe_subscription_id TEXT,
    status TEXT,
    current_period_end TIMESTAMP
);