from datetime import datetime
from sqlalchemy import Integer, String, Text, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
	pass

class Document(Base):
	__tablename__ = "documents"
	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	filename: Mapped[str] = mapped_column(String)
	content: Mapped[str] = mapped_column(Text)
	date_added: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
	word_count: Mapped[int] = mapped_column(Integer, default=0)
	line_count: Mapped[int] = mapped_column(Integer, default=0)