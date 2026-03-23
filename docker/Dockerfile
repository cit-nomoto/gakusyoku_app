# --- Litestream ビルドステージ ---
FROM python:3.12-slim AS litestream-builder

ENV LITESTREAM_VERSION=v0.3.13

RUN apt-get update && apt-get install -y --no-install-recommends wget \
    && wget -q -O /tmp/litestream.tar.gz \
       https://github.com/benbjohnson/litestream/releases/download/${LITESTREAM_VERSION}/litestream-${LITESTREAM_VERSION}-linux-amd64.tar.gz \
    && tar -C /usr/local/bin -xzf /tmp/litestream.tar.gz \
    && rm /tmp/litestream.tar.gz

# --- 本番イメージ ---
FROM python:3.12-slim
WORKDIR /app

# 依存パッケージをインストール
COPY gakusyoku_app/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションのソースをコピー
COPY gakusyoku_app/ ./

# Litestream CLI をコピー
COPY --from=litestream-builder /usr/local/bin/litestream /usr/local/bin/litestream

# litestream の設定ファイルと起動スクリプトをコピー
COPY docker/litestream.yml /etc/litestream.yml
COPY docker/run.sh ./
RUN chmod +x run.sh

# Cloud Run はポート 8080 を使用する
EXPOSE 8080

# 起動スクリプトを実行する
CMD ["/app/run.sh"]