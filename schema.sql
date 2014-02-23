drop table if exists user;
create table user (
  user_id integer primary key autoincrement,
  username text not null,
  email text not null,
  pw_hash text not null
);

drop table if exists api_key;
create table api_key (
  who_id integer,
  key text not null,
  secret text not null
);

drop table if exists message;
create table message (
  message_id integer primary key autoincrement,
  author_id integer not null,
  text text not null,
  pub_date integer
);

drop table if exists bot;
create table bot (
  bot_id integer primary key autoincrement,
  bot_name text not null,
  owner_id integer not null,
  trade_amount integer not null,
  floor integer not null,
  ceiling integer not null,
  abs_floor integer not null,
  abs_ceiling integer not null,
  algorithm text not null,
  status text not null
  );
