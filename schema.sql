-- DDL creates view and stored function to enable quick activity lookup by pid
-- tym@benchprep.com 2019-07-26


begin;
create or replace view timed_activity as 
select age(now(), xact_start) as xact_age 
     , age(now(), query_start) as query_age 
     , *
  from pg_stat_activity
 where backend_type = 'client backend';
 
drop function if exists pid_lookup;

create or replace function pid_lookup(pid integer) returns
 setof timed_activity as $$
select *
  from timed_activity
 where pid = (pid_lookup.pid);
 $$ language sql 
 volatile 
 security definer;
 
 ;commit;