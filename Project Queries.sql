show databases;
create database PRODUCTS;
USE PRODUCTS;
show tables;

CREATE TABLE flip_products(
title varchar(2000),
price varchar(2000)
);

CREATE TABLE dell_products(
title varchar(2000),
price varchar(2000)
);

CREATE TABLE croma_products(
title varchar(2000),
price varchar(2000)
);

CREATE TABLE rel_products(
title varchar(2000),
price varchar(2000)
);

select * from flip_products;
select count(*) from flip_products;

select * from dell_products;
select count(*) from dell_products;

select * from rel_products;
select count(*) from rel_products;

select * from croma_products;
select count(*) from croma_products;

select distinct count(title)
from croma_products;

SELECT title
FROM flip_products
WHERE title REGEXP '[^\x00-\x7F]';

SELECT title, price, 'flip_products' AS source_table
FROM flip_products
WHERE title LIKE '%ASUS Vivobook 15 %'

UNION ALL

SELECT title, price, 'croma_products' AS source_table
FROM croma_products
WHERE title LIKE '%ASUS Vivobook 15%'

UNION ALL

SELECT title, price, 'dell_products' AS source_table
FROM dell_products
WHERE title LIKE '%ASUS Vivobook 15%'

UNION ALL

SELECT title, price, 'rel_products' AS source_table
FROM rel_products
WHERE title LIKE '%ASUS Vivobook 15%';



SELECT title, price, 'flip_products' AS source_table
FROM flip_products
WHERE title LIKE '%Dell Insprion%'

UNION ALL

SELECT title, price, 'croma_products' AS source_table
FROM croma_products
WHERE title LIKE '%Dell Insprion%'

UNION ALL

SELECT title, price, 'dell_products' AS source_table
FROM dell_products
WHERE title LIKE '%Dell Insprion%'

UNION ALL

SELECT title, price, 'rel_products' AS source_table
FROM rel_products
WHERE title LIKE '%Dell Insprion%';


SET SQL_SAFE_UPDATES = 0;

DELETE FROM flip_products;
DELETE FROM rel_products;
DELETE FROM dell_products;
DELETE FROM croma_products;

SET SQL_SAFE_UPDATES = 1;


