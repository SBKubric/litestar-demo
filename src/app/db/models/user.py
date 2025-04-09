from __future__ import annotations

from datetime import datetime  # noqa: TC003

from advanced_alchemy.base import BigIntBase
from sqlalchemy import DateTime, String, func
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column


class User(BigIntBase):
    __tablename__ = "user_account"
    __table_args__ = {"comment": "User accounts"}

    email: Mapped[str] = mapped_column(String(length=255), unique=True, nullable=False)
    name: Mapped[str | None] = mapped_column(nullable=True, default=None)
    surname: Mapped[str | None] = mapped_column(nullable=True, default=None)
    hashed_password: Mapped[str | None] = mapped_column(String(length=255), nullable=True, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    @hybrid_property
    def has_password(self) -> bool:
        return self.hashed_password is not None
