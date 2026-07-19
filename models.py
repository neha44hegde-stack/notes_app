from datetime import datetime, timezone
from extensions import db


note_tags = db.Table(
    "note_tags",
    db.Column("note_id", db.Integer, db.ForeignKey("notes.id"), primary_key=True),
    db.Column("tag_id", db.Integer, db.ForeignKey("tags.id"), primary_key=True),
)


class User(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    notes = db.relationship(
        "Note", backref="user", lazy=True, cascade="all, delete"
    )
    categories = db.relationship(
        "Category", backref="user", lazy=True, cascade="all, delete"
    )
    tags = db.relationship(
        "Tag", backref="user", lazy=True, cascade="all, delete"
    )


class Category(db.Model):

    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    notes = db.relationship("Note", backref="category", lazy=True)

    __table_args__ = (
        db.UniqueConstraint("name", "user_id", name="uq_category_name_per_user"),
    )

    def to_dict(self):
        return {"id": self.id, "name": self.name}


class Tag(db.Model):

    __tablename__ = "tags"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    __table_args__ = (
        db.UniqueConstraint("name", "user_id", name="uq_tag_name_per_user"),
    )

    def to_dict(self):
        return {"id": self.id, "name": self.name}


class Attachment(db.Model):

    __tablename__ = "attachments"

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    note_id = db.Column(db.Integer, db.ForeignKey("notes.id"), nullable=False)

    uploaded_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "original_filename": self.original_filename,
            "uploaded_at": self.uploaded_at.isoformat(),
        }


class Note(db.Model):

    __tablename__ = "notes"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text, nullable=False)
    ai_summary = db.Column(db.Text, nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)

    is_pinned = db.Column(db.Boolean, default=False, nullable=False)
    is_archived = db.Column(db.Boolean, default=False, nullable=False)
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    tags = db.relationship(
        "Tag", secondary=note_tags, backref=db.backref("notes", lazy=True)
    )
    attachments = db.relationship(
        "Attachment", backref="note", lazy=True, cascade="all, delete"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "ai_summary": self.ai_summary,
            "user_id": self.user_id,
            "category": self.category.to_dict() if self.category else None,
            "tags": [tag.to_dict() for tag in self.tags],
            "attachments": [a.to_dict() for a in self.attachments],
            "is_pinned": self.is_pinned,
            "is_archived": self.is_archived,
            "is_deleted": self.is_deleted,
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }