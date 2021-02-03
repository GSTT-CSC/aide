FROM nginx

EXPOSE 80

COPY build/ /var/www/

COPY nginx_app.conf /etc/nginx/conf.d/default.conf
COPY server.conf /etc/nginx/nginx.conf
