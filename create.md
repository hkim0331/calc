# テーブル定義

```sql
drop table if exists calc;
create table calc (
       num1  integer default 0,
       num2  integer default 0,
       op    char(1)
);

insert into calc (num1, num2, op) values (0, 0, ' ');
```
