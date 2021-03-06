import logging

from google.cloud import bigquery

logger = logging.getLogger(__name__)


def list_tables(dataset_id):
    tables = bigquery.Client().list_tables(dataset_id)

    return {table.table_id for table in tables}


def compare(src_dataset_id, dest_dataset_id):
    equals = True  # init

    src_tables = list_tables(src_dataset_id)
    dest_tables = list_tables(dest_dataset_id)

    if src_tables.symmetric_difference(dest_tables):
        equals = False
        logger.info(
            f"These datasets contain the following symmetric difference: {src_tables ^ dest_tables}"
        )

    client = bigquery.Client()    
    tables_intersection = src_tables.intersection(dest_tables)

    for table in tables_intersection:
        src_table = client.get_table(f"{src_dataset_id}.{table}")
        dest_table = client.get_table(f"{dest_dataset_id}.{table}")

        if (
            src_table.num_rows == dest_table.num_rows
            and src_table.num_bytes == dest_table.num_bytes
        ):
            logger.debug(f"{src_dataset_id}.{table} equals {dest_dataset_id}.{table}")
        else:
            equals = False
            logger.info(
                f"{src_dataset_id}.{table} *doesn't* equal {dest_dataset_id}.{table}."
            )

            logger.info(
                f"Stats: the former contains {src_table.num_rows} rows totalling {src_table.num_bytes} bytes as compared to {dest_table.num_rows} rows & {dest_table.num_bytes} bytes."
            )

    return equals
