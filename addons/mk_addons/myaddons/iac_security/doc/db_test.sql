--清理某一个SC的供应商评鉴数据
--1.根据SC CODE查询SC ID
select * from iac_supplier_company a where a.company_no = 'SC000530';

--根据sc id查询评核名单和评核数据
select * from iac_score_list a where a.supplier_company_id = 3573;
select * from iac_score_part_category a where a.score_list_id in (643,644);
select * from iac_score_part_category_line a where a.score_part_category_id in (752,753);

--根据sc id查询评核名单，并删除评核名单打分数据
delete from iac_score_list a where a.supplier_company_id = 334;
delete from iac_score_part_category a where a.score_list_id in (643,644);
delete from iac_score_part_category_line a where a.score_part_category_id in (752,753);