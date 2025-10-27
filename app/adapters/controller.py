import logging
import tempfile
from fastapi import (
    APIRouter, UploadFile, File, Query, Response, Depends, HTTPException
    )
from fastapi.responses import JSONResponse
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.adapters.file_reader import FileReader
from app.database.session import get_db
from app.use_cases.order_service import OrderService
from app.use_cases.process_orders import OrderProcessor

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/orders", status_code=204)
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
            logger.debug(f"Uploaded file saved to temp path: {tmp_path}")

        file_reader = FileReader(file_path=tmp_path)
        processor = OrderProcessor(file_reader=file_reader)
        users = processor.execute()

        if not users:
            logger.info("No valid data found in file.")
            return Response(status_code=204)

        OrderService(db).save_users(users)
        return Response(status_code=204)
    except Exception as e:
        logger.exception("Failed to process uploaded file, error: %s", str(e))
        raise HTTPException(
            status_code=500,
            detail="Internal server error while processing file."
            )


@router.get("/orders")
def get_orders(
    order_id: Optional[int] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    try:
        orders_data = OrderService(db).get_orders(
            order_id=order_id,
            start_date=start_date,
            end_date=end_date
        )

        if not orders_data:
            if order_id is not None:
                raise HTTPException(status_code=404, detail=f"Order with ID {order_id} not found")
            return Response(status_code=204)

        return JSONResponse(content=orders_data)
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.exception(
            "Database error occurred during GET /orders. Exception: %s",
            str(e))
        raise HTTPException(status_code=500, detail="Database error.")
    except Exception as e:
        logger.exception(
            "Unexpected error occurred during GET /orders. Exception: %s",
            str(e))
        raise HTTPException(status_code=500, detail="Internal server error.")
