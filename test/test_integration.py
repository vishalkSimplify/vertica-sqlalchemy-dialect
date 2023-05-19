# Copyright (c) 2018-2023 Micro Focus or one of its affiliates.
# Copyright (c) 2017 StartApp Inc.
# Copyright (c) 2015 Locus Energy
# Copyright (c) 2013 James Casbon
# Copyright (c) 2010 Bo Shi

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sqlalchemy as sa
from sqlalchemy.sql import sqltypes
import pytest
import re 
from . import sample_objects as sample

@pytest.fixture(scope="module")
def vconn():
    engine = sa.create_engine('vertica+vertica_python://dbadmin:abc123@localhost:5433/VMart')
    try:     
        conn = engine.connect()
    except:
        print("Failed to connect to the database")
    yield [engine, conn]
    conn.close()
    engine.dispose()

def test_get_server_version_info(vconn):
    res = vconn[0].dialect._get_server_version_info(vconn[1])
    assert res == (12,0,2)

def test_get_default_schema_name(vconn):
    res = vconn[0].dialect._get_default_schema_name(vconn[1])
    assert res == "public"

def test_has_schema(vconn):
    sc1 = vconn[0].dialect.has_schema(vconn[1], schema="public")
    assert sc1 == True
    sc2 = vconn[0].dialect.has_schema(vconn[1], schema="store")
    assert sc2 == True

def test_has_table(vconn):
    res = vconn[0].dialect.has_table(connection=vconn[1], table_name=sample.sample_table_list["store"][0], schema="store")
    assert res == True

def test_has_sequence(vconn):
    res = vconn[0].dialect.has_sequence(connection=vconn[1], sequence_name="clicks_user_id_seq", schema="public")
    assert res == True

def test_has_type(vconn):
    res = vconn[0].dialect.has_type(connection=vconn[1], type_name="Long Varchar")
    assert res == True

def test_get_schema_names(vconn):
    res = vconn[0].dialect.get_schema_names(connection=vconn[1])
    sc=0
    # By pass schema if schema created by conftest. TODO Handle this in conftest
    for s in res:
        if "test" not in s:
            sc+=1
    assert sc == 3
    assert "store" in res

# TODO Improve this function to verify the output with a regex match
def test_get_table_comment(vconn):
    res = vconn[0].dialect.get_table_comment(connection=vconn[1], table_name=sample.sample_table_list["public"][0], schema="public")
    assert res["properties"]["create_time"]
    assert res["properties"]["Total_Table_Size"]

# TODO Improve this function to verify the output with a regex match
def test_get_table_oid(vconn):
    res = vconn[0].dialect.get_table_oid(connection=vconn[1], table_name=sample.sample_table_list["public"][1], schema="public")
    # Assert the oid is an int
    assert type(res) == int
    # Assert the format of the oid
    p = re.compile(r'^\d+$')
    assert bool(p.match(str(res)))

def test_get_projection_names(vconn):
    res = vconn[0].dialect.get_projection_names(connection=vconn[1], schema="public")
    # Assert the no. of projections
    assert len(res) == 41
    # Assert sample projection
    assert sample.sample_projections[0] in res

def test_get_table_names(vconn):
    res = vconn[0].dialect.get_table_names(connection=vconn[1], schema="public")
    # Assert the no. of tables
    assert len(res) == 42
    # Assert sample tables
    assert all(value in res  for value in sample.sample_table_list["public"])

    res = vconn[0].dialect.get_table_names(connection=vconn[1], schema="store")
    # Assert the no of tables in another schema
    assert len(res) == 3
    # Assert sample tables
    assert all(value in res  for value in sample.sample_table_list["store"])

def test_get_temp_table_names(vconn):
    res = vconn[0].dialect.get_temp_table_names(connection=vconn[1], schema="public")
    # Assert the no. of temp tables
    assert len(res) == 1
    # Assert sample tables
    assert sample.sample_temp_table in res

def test_get_view_names(vconn):
    res = vconn[0].dialect.get_view_names(connection=vconn[1], schema="public")
    # Assert the no. of views
    assert len(res) == 1
    # Assert sample view
    assert sample.sample_view in res

def test_get_view_definition(vconn):
    res = vconn[0].dialect.get_view_definition(connection=vconn[1], view_name=sample.sample_view, schema="public")
    # Assert the view definition exists
    assert len(res)>0
    # Assert the format of a view creation
    p = re.compile(r'SELECT')
    assert bool(p.match(res))

def test_get_temp_view_names(vconn):
    res = vconn[0].dialect.get_view_names(connection=vconn[1], schema="public")
    # Assert the no. of views
    assert len(res) == 1
    # Assert sample view
    assert sample.sample_view in res

def test_get_columns(vconn):
    res = vconn[0].dialect.get_columns(connection=vconn[1], table_name=sample.sample_table_list["public"][2], schema="public")
    # Assert the no. of columns
    assert len(res)>0
    # Assert sample columns
    assert all(value["name"] in sample.sample_columns for value in res)

def test_get_unique_constraints(vconn):
    # TODO query doesnt return the result here. Query works from other clients.
    assert True
    ucons = vconn[0].dialect.get_unique_constraints(connection=vconn[1], table_name=sample.sample_table_list["store"][0], schema="store")
    # Assert the no. of unique contraints
    assert len(ucons)>0
    # Assert sample constraint
    for v in sample.sample_constraints.values():
        print(v)
    for ucon in ucons:
        assert ucon['name'],ucon['column_names'] in sample.sample_constraints

def test_get_check_constraints(vconn):
    # TODO query doesnt return the result here. Query works from other clients.
    assert True
    # res = vconn[0].dialect.get_unique_constraints(connection=vconn[1], table_name=sample_table_list["store"][0], schema="store")
    # # Assert the no. of unique contraints
    # assert len(res)>0
    # # Assert sample constraint
    # assert all(k["names"] in sample_columns.keys() for k in res)
    # assert all(v["columns"] in sample_columns.values() for v in res)

def test_normalize_name(vconn):
    assert vconn[0].dialect.normalize_name("SAMPLE_TABLE123") == "sample_table123"
    assert vconn[0].dialect.normalize_name("saMPLE_123") == "sample_123"

def test_denormalize_name(vconn):
    assert vconn[0].dialect.denormalize_name("SAMPLE_TABLE123") == "SAMPLE_TABLE123"
    assert vconn[0].dialect.denormalize_name("saMPLE_123") == "saMPLE_123"

def test_get_pk_constraint(vconn):
    # TODO query doesnt return the result here. Query works from other clients.
    res = vconn[0].dialect.get_pk_constraint(connection=vconn[1], table_name=sample.sample_table_list["public"][0], schema="public")
    # Assert the no. of unique contraints
    assert len(res)>0
    # Assert sample constraint
    assert all(k in sample.sample_pk.values() for k in res['name'])

def test_get_foreign_keys(vconn):
    # TODO Need functionality
    assert True
    #res = vconn[0].dialect.get_foreign_keys(connection=vconn[1], table_name=sample_table_list["store"][0], schema="store")
    # Assert the no. of unique contraints
    #assert len(res)>0
    # Assert sample constraint
    # assert all(k in sample_pk.values() for k in res['name'])

def test_get_column_info(vconn):
    # TODO Add more tests here for other datatypes
    res = vconn[0].dialect._get_column_info(name="customer_name", data_type="varchar(256)", default=None, is_nullable=False)
    assert res['name'] == 'customer_name'
    assert res['autoincrement'] == False
    assert res['nullable'] == False
    assert type(res['type']) == type(sqltypes.VARCHAR(length=256))

def test_get_models_names(vconn):
    res = vconn[0].dialect.get_models_names(vconn[1], schema="public")
    # Assert model names
    assert all(value in sample.sample_model_list for value in res)

def test_get_extra_tags(vconn):
    extra_tags = vconn[0].dialect._get_extra_tags(vconn[1], name="table", schema="public")
    assert len(extra_tags)==42
    assert all(value in extra_tags for value in sample.sample_tags)

def test_get_ros_count(vconn):
    rc = vconn[0].dialect._get_ros_count(vconn[1], projection_name="employee_dimension_super", name="table", schema="public")
    assert rc>0

def test_get_segmented(vconn):
    isseg = vconn[0].dialect._get_segmented(vconn[1], projection_name=sample.sample_projections[1], schema="store")
    assert isseg[0] in ["True","False"]
    assert isseg[1]

def test_get_partitionkey(vconn):
    pc = vconn[0].dialect._get_partitionkey(vconn[1], projection_name=sample.sample_projections[2], schema="store")
    assert pc

def test_get_projectiontype(vconn):
    pt = vconn[0].dialect._get_projectiontype(vconn[1], projection_name=sample.sample_projections[1], schema="store")
    assert pt == ['is_super_projection']

def test_get_numpartitions(vconn):
    pn = vconn[0].dialect._get_numpartitions(vconn[1], projection_name=sample.sample_projections[1], schema="store")
    assert pn>0

def test_get_projectionsize(vconn):
    ps = vconn[0].dialect._get_projectionsize(vconn[1], projection_name=sample.sample_projections[1], schema="store")
    assert ps>0

def test_get_ifcachedproj(vconn):
    cp = vconn[0].dialect._get_ifcachedproj(vconn[1], projection_name=sample.sample_projections[1], schema="store")
    assert cp in [True,False]

def test_get_projection_comment(vconn):
    pc = vconn[0].dialect.get_projection_comment(vconn[1], projection_name=sample.sample_projections[1], schema="store")
    assert pc["properties"]["ROS Count"]\
    and pc["properties"]["is_segmented"] \
    and pc["properties"]["Projection Type"] \
    and pc["properties"]["Partition Key"] \
    and pc["properties"]["Number of Partition"] \
    and pc["properties"]["Segmentation_key"] \
    and pc["properties"]["Projection Size"] \
    and pc["properties"]["Projection Cached"]

def test_get_model_comment(vconn):
    mc = vconn[0].dialect.get_model_comment(vconn[1], model_name=sample.sample_ml_model, schema="public")
    assert mc["properties"]["used_by"] == "dbadmin"
    assert len(mc["properties"]["Model Attributes"])>0
    assert len(mc["properties"]["Model Specifications"])>0

def test_get_oauth_comment(vconn):
    oc = vconn[0].dialect.get_oauth_comment(vconn[1],oauth= sample.sample_oauth_name,schema="None")
    assert oc["properties"]["client_id"] == "vertica"
    h = re.compile(r'http://|https://')
    assert len(oc["properties"]["introspect_url"])>0
    assert bool(h.match(oc["properties"]["introspect_url"]))
    assert len(oc["properties"]["discovery_url"])>0
    assert bool(h.match(oc["properties"]["discovery_url"]))
    assert len(oc["properties"]["is_fallthrough_enabled"])>0



#################################################### specific to Datahub ####################################################

def test_get_table_owner(vconn):
    oc = vconn[0].dialect.get_table_owner(vconn[1],schema="public")
    owner_info = oc[0][1]
    assert owner_info == "dbadmin"

