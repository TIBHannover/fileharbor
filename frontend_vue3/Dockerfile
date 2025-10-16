FROM nginx:1.29.2-alpine

RUN apk add --update npm git
RUN npm install -g npm@11.6.2
COPY ./default.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
WORKDIR /app/frontend

CMD ["nginx", "-g", "daemon off;"]
