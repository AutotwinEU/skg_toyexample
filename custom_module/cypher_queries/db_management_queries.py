from promg import Query

class DBManagementQueries:
    @staticmethod
    def create_db(dbname):
        query_str = '''CREATE OR REPLACE DATABASE $dbname'''
        return Query(query_str=query_str, template_string_parameters={"dbname": dbname} )

    @staticmethod
    def drop_db(dbname):
        query_str = '''DROP DATABASE $dbname'''
        return Query(query_str=query_str, template_string_parameters={"dbname": dbname} )

    @staticmethod
    def return_db_list():
        query_str = '''show database yield name'''
        return Query(query_str=query_str)