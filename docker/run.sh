#!/bin/sh

set -e

# instance ディレクトリを作成する (SQLite のデータベースファイルの保存先)
mkdir -p /app/instance

# もしローカルに古いデータベースファイルが存在していたら削除する
rm -f /app/instance/app.db

# Google Cloud Storage からデータベースファイルを復元する
# `-if-replica-exists` フラグを指定すると、レプリカが存在する場合にのみ復元を行う
# これを指定しないと、まだレプリカが存在しない場合 ( = 初回起動時 ) にエラーが発生する
litestream restore -if-replica-exists -config /etc/litestream.yml /app/instance/app.db

# Google Cloud Storage にデータベースファイルをレプリケートしながら Gunicorn でアプリを起動する
litestream replicate -config /etc/litestream.yml \
  -exec "gunicorn --bind 0.0.0.0:8080 --workers 1 main:app"