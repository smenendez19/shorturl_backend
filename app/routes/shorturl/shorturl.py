# ShortURL endpoints

# Imports
import logging
from datetime import datetime

# FastAPI
from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import ORJSONResponse, RedirectResponse

# Database
from sqlmodel import Session, select

# Load settings
from app.config.config import Settings
from app.db.database import get_session

# Pydantic models
from app.models.body.shorturl import ShortURLBody, ShortURLBuildBody
from app.models.sql.shorturl import ShortURL
from app.utils.get_settings import get_settings

# Utils
from app.utils.shorturl.shorturl_tools import convert_long_url_short_id

# Start Router
router = APIRouter(prefix="/v1")


@router.post(
    "/shorturl/build",
    status_code=status.HTTP_200_OK,
    tags=["ShortURL"],
    responses={
        200: {
            "description": "Successful Response",
            "content": {
                "application/json": {"example": {"message": "ShortURL created successfully", "short_url": "http://localhost:8000/v1/LTMGmJ3"}}
            },
        },
        422: {
            "description": "Unprocessable Entity",
            "content": {"application/json": {"example": {"errors": [{"msg": "Field is required", "loc": "body.url", "type": "missing"}]}}},
        },
    },
)
def build_shorturl(
    body: ShortURLBuildBody,
    request: Request,
    settings: Settings = Depends(get_settings),
    session: Session = Depends(get_session),
):
    """
    Builds a shortURL with the body parameters
    """
    # Create shortURL
    logging.info(f"Building shortURL for URL {body.url}")
    short_url_id = convert_long_url_short_id(body.url)

    # Save in database
    logging.info("Saving new shortURL in database")
    row = ShortURL(id=short_url_id, url=body.url, expires_at=body.expires_at)

    with session:
        session.add(row)
        session.commit()

    logging.info(f"ShortURL {short_url_id} created successfully")
    logging.info("Returning API status")

    return ORJSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "ShortURL created successfully",
            "short_url": f"{request.base_url}{router.prefix[1:]}/{short_url_id}",
        },
    )


@router.get(
    "/shorturl/all",
    status_code=status.HTTP_200_OK,
    tags=["ShortURL"],
    responses={
        200: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {
                        "data": [
                            {
                                "url": "https://twitter.com/home",
                                "created_at": "2024-03-12T00:26:08.162936",
                                "expires_at": "2024-03-11T00:00:00",
                                "updated_at": "2024-03-12T00:26:08.162936",
                                "visitors": 0,
                                "id": "WvCxUB8",
                            },
                        ],
                        "count": 1,
                        "page": 1,
                        "limit": 10,
                    }
                }
            },
        },
    },
)
def get_all_shorturl(
    request: Request, settings: Settings = Depends(get_settings), session: Session = Depends(get_session), page: int = 1, limit: int = 5
):
    """
    Get all shorturl in the database paginated
    """

    # Convert to default if less than 1
    if page < 1:
        page = 1

    if limit < 5:
        limit = 5

    logging.debug(f"Page: {page} Limit: {limit}")

    with session:
        query = select(ShortURL).offset((page - 1) * limit).limit(limit)
        results = session.exec(query).all()

    return ORJSONResponse(
        status_code=status.HTTP_200_OK,
        content={"data": [short_url.model_dump() for short_url in results], "count": len(results), "page": page, "limit": limit},
    )


@router.get(
    "/{short_url_id}",
    status_code=status.HTTP_302_FOUND,
    tags=["ShortURL"],
    responses={
        302: {
            "description": "Redirect successful",
            "content": {"application/json": {"example": {"message": "Redirecting to URL"}}},
        },
        404: {
            "description": "ShortURL not found",
            "content": {"application/json": {"example": {"message": "ShortURL not found"}}},
        },
    },
)
def redirect_shorturl(short_url_id, request: Request, settings: Settings = Depends(get_settings), session: Session = Depends(get_session)):
    """
    Redirect the existing short URL to the original URL and save last visitor
    """

    # Get shorturl from database
    logging.info(f"Getting ShortURL {short_url_id} from database")
    with session:
        query = select(ShortURL).where(ShortURL.id == short_url_id)
        results = session.exec(query)
        short_url = results.first()
        if short_url is None:
            logging.error(f"ShortURL {short_url_id} not found")
            return ORJSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"message": "ShortURL not found"},
            )

        # Update visitors and get original URL
        logging.info(f"Redirecting to original URL {short_url.url}")
        short_url.visitors = short_url.visitors + 1
        original_url = short_url.url
        session.add(short_url)
        session.commit()

    logging.info("Returning API status")

    # Response
    return RedirectResponse(url=original_url, status_code=status.HTTP_302_FOUND)


@router.get(
    "/shorturl/{short_url_id}",
    status_code=status.HTTP_200_OK,
    tags=["ShortURL"],
    responses={
        200: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {
                        "data": {
                            "id": "LTMGmJ3",
                            "url": "https://twitter.com/home",
                            "visitors": 5,
                            "created_at": "2024-03-09T23:34:44.386857",
                            "updated_at": "2024-03-09T23:34:44.386857",
                            "expires_at": None,
                        },
                    },
                }
            },
        },
        404: {
            "description": "ShortURL not found",
            "content": {"application/json": {"example": {"message": "ShortURL not found"}}},
        },
    },
)
def get_shorturl_details(short_url_id, request: Request, settings: Settings = Depends(get_settings), session: Session = Depends(get_session)):
    """
    Get shortURL data
    """

    # Get shortURL from database
    logging.info(f"Getting shortURL{short_url_id} from database")
    with session:
        query = select(ShortURL).where(ShortURL.id == short_url_id)
        results = session.exec(query)
        short_url = results.first()
        if short_url is None:
            logging.error(f"ShortURL {short_url_id} not found")
            return ORJSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"message": "shortURL not found"},
            )

        logging.info(f"Returning shortURL {short_url_id} stats")
        logging.info("Returning API status")

        return ORJSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "data": {
                    "id": short_url.id,
                    "url": short_url.url,
                    "visitors": short_url.visitors,
                    "created_at": short_url.created_at,
                    "updated_at": short_url.updated_at,
                    "expires_at": short_url.expires_at,
                }
            },
        )


@router.delete(
    "/shorturl/{short_url_id}",
    status_code=status.HTTP_200_OK,
    tags=["ShortURL"],
    responses={
        200: {
            "description": "Successful Response",
            "content": {"application/json": {"example": {"message": "ShortURL deleted successfully"}}},
        },
        404: {
            "description": "ShortURL not found",
            "content": {"application/json": {"example": {"message": "ShortURL not found"}}},
        },
    },
)
def delete_shorturl(short_url_id, request: Request, settings: Settings = Depends(get_settings), session: Session = Depends(get_session)):
    """
    Delete shortURL with id
    """

    # Get shorturl from database
    logging.info(f"Getting shortURL {short_url_id} from database")
    with session:
        query = select(ShortURL).where(ShortURL.id == short_url_id)
        results = session.exec(query)
        short_url = results.first()
        if short_url is None:
            logging.error(f"ShortURL {short_url_id} not found")
            return ORJSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"message": "ShortURL not found"},
            )

        # Delete shortURL
        logging.info(f"Deleting shortURL {short_url_id} from database")
        session.delete(short_url)
        session.commit()

        logging.info(f"ShortURL {short_url_id} deleted successfully")
        logging.info("Returning API status")

    return ORJSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "ShortURL deleted successfully"},
    )


@router.put(
    "/shorturl/{short_url_id}",
    status_code=status.HTTP_200_OK,
    tags=["ShortURL"],
    responses={
        200: {
            "description": "Successful Response",
            "content": {"application/json": {"example": {"message": "ShortURL updated"}}},
        },
        404: {
            "description": "ShortURL not found",
            "content": {"application/json": {"example": {"message": "ShortURL not found"}}},
        },
    },
)
def update_shorturl(
    short_url_id, body: ShortURLBody, request: Request, settings: Settings = Depends(get_settings), session: Session = Depends(get_session)
):
    """
    Update shortURL object passing new parameters
    If url changes the visitors count is reset to 0
    """

    # Get shorturl from database
    logging.info(f"Getting shortURL {short_url_id} from database")
    with session:
        query = select(ShortURL).where(ShortURL.id == short_url_id)
        results = session.exec(query)
        short_url = results.first()
        if short_url is None:
            logging.error(f"ShortURL {short_url_id} not found")
            return ORJSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"message": "ShortURL not found"},
            )

        # Update with parameters
        logging.info(f"Updating shortURL {short_url_id} with new parameters")

        if body.url is not None:
            short_url.url = body.url
            short_url.visitors = 0
        if body.expires_at is not None:
            short_url.expires_at = body.expires_at

        short_url.updated_at = datetime.now()

        session.add(short_url)
        session.commit()

        logging.info(f"ShortURL {short_url_id} updated successfully")
        logging.info("Returning API status")

    return ORJSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "ShortURL updated"},
    )


@router.patch(
    "/shorturl/{short_url_id}",
    status_code=status.HTTP_200_OK,
    tags=["ShortURL"],
    responses={
        200: {
            "description": "Successful Response",
            "content": {"application/json": {"example": {"message": "ShortURL expire date updated"}}},
        },
        404: {
            "description": "ShortURL not found",
            "content": {"application/json": {"example": {"message": "ShortURL not found"}}},
        },
    },
)
def update_expire_date_shorturl(
    short_url_id, expire_date: datetime, request: Request, settings: Settings = Depends(get_settings), session: Session = Depends(get_session)
):
    """
    Updates expire date of shortURL
    """

    # Check expire date
    if expire_date is None or expire_date == "":
        logging.error("Expire date is empty")
        return ORJSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Expire date is empty"},
        )
    if expire_date < datetime.now():
        logging.error(f"Expire date {expire_date} is in the past")
        return ORJSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Expire date is in the past"},
        )

    # Get shorturl from database
    logging.info(f"Getting shortURL {short_url_id} from database")
    with session:
        query = select(ShortURL).where(ShortURL.id == short_url_id)
        results = session.exec(query)
        short_url = results.first()
        if short_url is None:
            logging.error(f"ShortURL {short_url_id} not found")
            return ORJSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"message": "ShortURL not found"},
            )

        # Update with parameters
        logging.info(f"Updating shortURL {short_url_id} with new expire date")

        short_url.expires_at = expire_date
        short_url.updated_at = datetime.now()
        session.add(short_url)
        session.commit()

        logging.info(f"ShortURL {short_url_id} expire date updated successfully")
        logging.info("Returning API status")

    return ORJSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "ShortURL expire date updated"},
    )
