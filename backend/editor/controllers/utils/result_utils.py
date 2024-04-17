from fastapi import HTTPException
from neo4j import AsyncResult, Record


async def get_unique_record(result: AsyncResult, record_id: str | None = None) -> Record:
    """
    Gets the unique record from a Cypher query result

    Raises:
        404 HTTPException: If no record is found
        500 HTTPException: If multiple records are found
    """
    record = await result.fetch(1)
    if record is None:
        exception_message = f"Record {record_id} not found" if record_id else "Record not found"
        raise HTTPException(status_code=404, detail=exception_message)

    remaining_record = await result.peek()
    if remaining_record is not None:
        exception_message = (
            f"Multiple records with id {record_id} found" if record_id else "Multiple records found"
        )
        raise HTTPException(
            status_code=500,
            detail=exception_message,
        )

    return record[0]
