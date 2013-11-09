create table groups (
  Id integer primary key autoincrement,
  Title text not null,
  MemberName text not null
);

create table members (
  MId integer primary key autoincrement,
  Title text not null,
  Delay integer not null
);
