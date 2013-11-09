drop table if exists entries;
create table entries (
  id integer primary key autoincrement,
  group_title text not null,
  member text not null
);
