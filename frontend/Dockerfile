# static site – no Node build needed
FROM nginx:alpine

# if you have an Nginx vhost file, ship it (optional)
# comment this line out if your nginx.conf is a full nginx.conf, not a site file
COPY nginx.conf /etc/nginx/conf.d/default.conf

# copy the static assets
COPY . /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
