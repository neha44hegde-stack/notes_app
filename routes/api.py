from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
)
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db, limiter
from models import User, Note, Tag, Category

api_bp = Blueprint("api", __name__, url_prefix="/api")


# ---------- AUTH ----------


@api_bp.route("/auth/register", methods=["POST"])
@limiter.limit("5 per minute")
def api_register():
    """
    Register a new user via the API
    ---
    tags:
      - Auth
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required: [username, email, password]
          properties:
            username: {type: string}
            email: {type: string}
            password: {type: string}
    responses:
      201:
        description: User created
      400:
        description: Email already exists
    """
    data = request.get_json() or {}
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"error": "username, email, and password are required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 400

    user = User(
        username=username,
        email=email,
        password=generate_password_hash(password),
    )
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User created", "user_id": user.id}), 201


@api_bp.route("/auth/login", methods=["POST"])
@limiter.limit("10 per minute")
def api_login():
    """
    Log in and receive a JWT access token
    ---
    tags:
      - Auth
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required: [email, password]
          properties:
            email: {type: string}
            password: {type: string}
    responses:
      200:
        description: Returns access_token
      401:
        description: Invalid credentials
    """
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        return jsonify({"error": "Invalid email or password"}), 401

    access_token = create_access_token(identity=str(user.id))
    return jsonify({"access_token": access_token, "username": user.username}), 200


# ---------- NOTES ----------


@api_bp.route("/notes", methods=["GET"])
@jwt_required()
def get_notes():
    """
    Get all notes for the logged-in user (paginated)
    ---
    tags:
      - Notes
    security:
      - Bearer: []
    parameters:
      - in: query
        name: view
        type: string
        enum: [active, archived, trash]
      - in: query
        name: q
        type: string
      - in: query
        name: page
        type: integer
      - in: query
        name: per_page
        type: integer
    responses:
      200:
        description: Paginated list of notes
    """
    user_id = int(get_jwt_identity())
    view = request.args.get("view", "active")
    query_text = request.args.get("q", "").strip()
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    query = Note.query.filter_by(user_id=user_id)

    if view == "trash":
        query = query.filter_by(is_deleted=True)
    else:
        query = query.filter_by(is_deleted=False)
        query = query.filter_by(is_archived=(view == "archived"))

    if query_text:
        like = f"%{query_text}%"
        query = query.filter((Note.title.ilike(like)) | (Note.description.ilike(like)))

    pagination = query.order_by(Note.is_pinned.desc(), Note.updated_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return (
        jsonify(
            {
                "notes": [note.to_dict() for note in pagination.items],
                "page": pagination.page,
                "per_page": pagination.per_page,
                "total_pages": pagination.pages,
                "total_items": pagination.total,
            }
        ),
        200,
    )


@api_bp.route("/notes/<int:note_id>", methods=["GET"])
@jwt_required()
def get_note(note_id):
    """
    Get a single note by ID
    ---
    tags:
      - Notes
    security:
      - Bearer: []
    parameters:
      - in: path
        name: note_id
        type: integer
        required: true
    responses:
      200:
        description: The note
      403:
        description: Not your note
      404:
        description: Note not found
    """
    user_id = int(get_jwt_identity())
    note = Note.query.get_or_404(note_id)

    if note.user_id != user_id:
        return jsonify({"error": "Forbidden"}), 403

    return jsonify(note.to_dict()), 200


@api_bp.route("/notes", methods=["POST"])
@jwt_required()
def create_note():
    """
    Create a new note
    ---
    tags:
      - Notes
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required: [title, description]
          properties:
            title: {type: string}
            description: {type: string}
            category_id: {type: integer}
            tags:
              type: array
              items: {type: string}
    responses:
      201:
        description: Note created
    """
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    title = data.get("title")
    description = data.get("description")

    if not title or not description:
        return jsonify({"error": "title and description are required"}), 400

    note = Note(
        title=title,
        description=description,
        user_id=user_id,
        category_id=data.get("category_id"),
    )

    tag_names = data.get("tags", [])
    tags = []
    for name in tag_names:
        name = name.strip().lower()
        if not name:
            continue
        tag = Tag.query.filter_by(name=name, user_id=user_id).first()
        if not tag:
            tag = Tag(name=name, user_id=user_id)
            db.session.add(tag)
            db.session.flush()
        tags.append(tag)
    note.tags = tags

    db.session.add(note)
    db.session.commit()

    return jsonify(note.to_dict()), 201


@api_bp.route("/notes/<int:note_id>", methods=["PUT"])
@jwt_required()
def update_note(note_id):
    """
    Update an existing note
    ---
    tags:
      - Notes
    security:
      - Bearer: []
    parameters:
      - in: path
        name: note_id
        type: integer
        required: true
      - in: body
        name: body
        schema:
          type: object
          properties:
            title: {type: string}
            description: {type: string}
            category_id: {type: integer}
            is_pinned: {type: boolean}
            is_archived: {type: boolean}
    responses:
      200:
        description: Note updated
      403:
        description: Not your note
    """
    user_id = int(get_jwt_identity())
    note = Note.query.get_or_404(note_id)

    if note.user_id != user_id:
        return jsonify({"error": "Forbidden"}), 403

    data = request.get_json() or {}

    if "title" in data:
        note.title = data["title"]
    if "description" in data:
        note.description = data["description"]
    if "category_id" in data:
        note.category_id = data["category_id"]
    if "is_pinned" in data:
        note.is_pinned = bool(data["is_pinned"])
    if "is_archived" in data:
        note.is_archived = bool(data["is_archived"])

    db.session.commit()
    return jsonify(note.to_dict()), 200


@api_bp.route("/notes/<int:note_id>", methods=["DELETE"])
@jwt_required()
def delete_note_api(note_id):
    """
    Move a note to trash (soft delete)
    ---
    tags:
      - Notes
    security:
      - Bearer: []
    parameters:
      - in: path
        name: note_id
        type: integer
        required: true
    responses:
      200:
        description: Note moved to trash
      403:
        description: Not your note
    """
    from datetime import datetime, timezone

    user_id = int(get_jwt_identity())
    note = Note.query.get_or_404(note_id)

    if note.user_id != user_id:
        return jsonify({"error": "Forbidden"}), 403

    note.is_deleted = True
    note.deleted_at = datetime.now(timezone.utc)
    db.session.commit()

    return jsonify({"message": "Note moved to trash"}), 200


# ---------- CATEGORIES ----------


@api_bp.route("/categories", methods=["GET"])
@jwt_required()
def get_categories():
    """
    Get all categories for the logged-in user
    ---
    tags:
      - Categories
    security:
      - Bearer: []
    responses:
      200:
        description: List of categories
    """
    user_id = int(get_jwt_identity())
    categories = Category.query.filter_by(user_id=user_id).all()
    return jsonify([c.to_dict() for c in categories]), 200


@api_bp.route("/categories", methods=["POST"])
@jwt_required()
def create_category():
    """
    Create a new category
    ---
    tags:
      - Categories
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required: [name]
          properties:
            name: {type: string}
    responses:
      201:
        description: Category created
    """
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    name = data.get("name")

    if not name:
        return jsonify({"error": "name is required"}), 400

    if Category.query.filter_by(name=name, user_id=user_id).first():
        return jsonify({"error": "Category already exists"}), 400

    category = Category(name=name, user_id=user_id)
    db.session.add(category)
    db.session.commit()

    return jsonify(category.to_dict()), 201


# ---------- TAGS ----------


@api_bp.route("/tags", methods=["GET"])
@jwt_required()
def get_tags():
    """
    Get all tags for the logged-in user
    ---
    tags:
      - Tags
    security:
      - Bearer: []
    responses:
      200:
        description: List of tags
    """
    user_id = int(get_jwt_identity())
    tags = Tag.query.filter_by(user_id=user_id).all()
    return jsonify([t.to_dict() for t in tags]), 200
