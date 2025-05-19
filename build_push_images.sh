#!/bin/bash

# Параметры
USERNAME="nikaivanova"
FRONTEND_IMAGE="foodgram-frontend"
BACKEND_IMAGE="foodgram-backend"
VERSION="latest"

echo "Аутентификация в Docker Hub"
docker login

echo "Сборка и публикация frontend образа"
docker build -t $USERNAME/$FRONTEND_IMAGE:$VERSION ./frontend
docker push $USERNAME/$FRONTEND_IMAGE:$VERSION

echo "Сборка и публикация backend образа"
docker build -t $USERNAME/$BACKEND_IMAGE:$VERSION ./backend
docker push $USERNAME/$BACKEND_IMAGE:$VERSION

echo "Образы успешно опубликованы:"
echo "$USERNAME/$FRONTEND_IMAGE:$VERSION"
echo "$USERNAME/$BACKEND_IMAGE:$VERSION"

echo "Обновление docker-compose.yml для использования опубликованных образов"
sed -i "s|build: ../frontend|image: $USERNAME/$FRONTEND_IMAGE:$VERSION|g" ./infra/docker-compose.yml
sed -i "s|build:|image: $USERNAME/$BACKEND_IMAGE:$VERSION\\n    # build:|g" ./infra/docker-compose.yml
sed -i "/context:/d" ./infra/docker-compose.yml
sed -i "/dockerfile:/d" ./infra/docker-compose.yml

echo "Готово! Теперь можно запускать проект с помощью docker-compose в папке infra" 