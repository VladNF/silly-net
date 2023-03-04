-- 
-- depends: 20230202_01_init
create index idx_first_last_name on users (lower(first_name) text_pattern_ops, lower(last_name) text_pattern_ops);
analyse users;

