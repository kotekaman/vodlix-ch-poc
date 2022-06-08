import queue

from fastapi import Query
from queries.ddl import ddl
from config.config import Config


class DDLServices(object):
    def __init__(self):
        self.query = ddl.Ddl()
        self.db = Config()
        self.db.init()

    def create_database(self, db_name):
        query = self.query.create_database(db_name)
        self.db.execute_query(query)

    def create_table(self, db_name, tb_name):

        query = self.query.create_table(tb_name, db_name)
        insert_query_ddl = self.query.insert_into_ddl_history()

        self.db.execute_query(query)
        self.db.insert_data(
            insert_query_ddl, [{'db_name': db_name, 'tb_name': tb_name}]
        )
    
    def create_table_with_columns(self, payload):
        db_name = payload["db_name"] 
        tb_name = payload["tb_name"]
        columns = payload["columns"]
        order_by = payload["order_by"]

        list_columns = []

        for column in columns.keys():
            list_columns.append("{} {}".format(column, columns[column]))
        
        fixed_columns = ",".join(list_columns)

        query = self.query.create_table_with_columns(tb_name,db_name,fixed_columns,order_by)
        self.db.execute_query(query)
    
    def insert_data(self,payload):
        db_name = payload["db_name"] 
        tb_name = payload["tb_name"]
        datas = payload["datas"]

        list_columns = []

        for column in datas.keys():
            list_columns.append(column)
        
        fixed_columns = "("+",".join(list_columns)+")"
        
        query = self.query.insert_data_to_table(db_name,tb_name,fixed_columns)
        self.db.insert_data(query,[datas])
        

    def selec_data_from_table(self,db_name,tb_name,column,limit="",offset=""):
        
        columns = column.columns
        if limit == "" or offset =="":
            limit="10000"
            offset="0"

        query = self.query.select_datas(columns,db_name,tb_name,limit,offset)
        self.db.execute_query(query)
        datas = self.db.cursor.fetchall()

        data_responses = []

        for data in datas:
            datas_dict = {}
            for index in range(len(columns)):
                datas_dict[columns[index]] = data[index]
            data_responses.append(datas_dict)

        return data_responses

    def create_ddl_history_table(self):
        self.db.execute_query(self.query.create_ddl_database())
        self.db.execute_query(self.query.create_ddl_history_table())
    
    def delete_table(self,db_name,tb_name):
        query = self.query.delete_table(db_name,tb_name)
        self.db.execute_query(query)
    
    def alter_table(self,payload):
        tb_name = payload["tb_name"]
        db_name = payload["db_name"]
        column_name = payload["column_name"]
        operation_type = payload["operation_type"]

        self.db.execute_query(self.query.use_db(db_name))

        if operation_type == "ADD":

            data_type = payload["data_type"]
            query = self.query.add_new_column(tb_name,column_name,data_type)

        elif operation_type == "DELETE":
            query = self.query.delete_column(tb_name,column_name)

        self.db.execute_query(query)
