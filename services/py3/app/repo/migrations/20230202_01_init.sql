-- 
-- depends: 
create table users
(
    user_id    varchar(32) primary key,
    email      text unique,
    first_name text,
    last_name  text,
    age        integer,
    bio        text,
    city       text,
    pwd_hash   text
);
