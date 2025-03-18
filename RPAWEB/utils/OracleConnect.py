import oracledb 


def get_db_connection():
    dsn_tns = oracledb.makedsn(
        'appmagic.diamond.co.id', '1521', service_name='AROBS')
    conn = oracledb.connect(
        user='b2brobotik', password='b2brobotik12345', dsn=dsn_tns)
    return conn
