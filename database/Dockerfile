# Database Dockerfile with pre-seeded sales dataset (5,840 rows)
FROM mysql:8.0

# Set default character set
ENV MYSQL_DATABASE=salesdb
ENV MYSQL_ROOT_PASSWORD=password

# Copy initialization script
COPY init.sql /docker-entrypoint-initdb.d/01-init.sql

EXPOSE 3306
