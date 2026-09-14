import os
from typing import Annotated
from fastapi import Depends, Header, HTTPException, Query, status
from sqlmodel import Session
from .database import get_session


API_KEY = os.getenv("TASK_API_KEY", "demo-secret-key")




SessionDep = Annotated[Session, Depends(get_session)]

def require_api_key(api_key: Annotated[str, Header()]) -> None:
    """
    A request with no api key header at all never reaches this function. It should result to 422 error which is reaised automatically because header parameter is required for this request. A request with the header but the wrong value gets a 401 from the explicit check below, since FastAPI has no way to know which value counts as "correct."
    """
    if api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key"
        )

APIKeyDep = Annotated[None, Depends(require_api_key)]



class PaginationParams:
    """
    A dependency class: FastAPI instantiates this with the incoming query parameters as constructor arguments, the same way it'd call a plain dependency function. This is just a convenient way to bundle several related query parameters (with validation) into one reusable object.
    """

    def __init__(
            self,
            offset: Annotated[int, Query(ge=0, description="Number of records to skip")] = 0,
            limit: Annotated[int, Query(ge=1, le=100, description="Max records to return")] = 20
    ) -> None:
        self.offset = offset
        self.limit = limit


PaginationDep = Annotated[PaginationParams, Depends(PaginationParams)]