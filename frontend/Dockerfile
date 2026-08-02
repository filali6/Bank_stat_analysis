# Étape 1 : build de l'application Angular
FROM node:20-alpine AS build

WORKDIR /app
COPY package*.json ./
RUN npm ci

COPY . .
RUN npx ng build

# Étape 2 : servir les fichiers statiques avec nginx (léger, standard pour du prod)
FROM nginx:alpine

COPY --from=build /app/dist/frontend/browser /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
