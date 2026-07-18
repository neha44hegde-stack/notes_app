from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

from extensions import db
from models import Note, Tag, Category

notes_bp = Blueprint("notes", __name__)


def _get_or_create_tags(tag_names, user_id):
    """Given a list of tag name strings, fetch existing tags or create new ones."""
    tags = []
    for name in tag_names:
        name = name.strip().lower()
        if not name:
            continue
        tag = Tag.query.filter_by(name=name, user_id=user_id).first()
        if not tag:
            tag = Tag(name=name, user_id=user_id)
            db.session.add(tag)
            db.session.flush()  # so tag.id is available before commit
        tags.append(tag)
    return tags


@notes_bp.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        flash("You must be logged in to view this page", "warning")
        return redirect(url_for("auth.login"))

    user_id = session["user_id"]
    view = request.args.get("view", "active")  # active | archived | trash
    query_text = request.args.get("q", "").strip()
    category_id = request.args.get("category_id", type=int)
    tag_id = request.args.get("tag_id", type=int)

    query = Note.query.filter_by(user_id=user_id)

    if view == "trash":
        query = query.filter_by(is_deleted=True)
    else:
        query = query.filter_by(is_deleted=False)
        if view == "archived":
            query = query.filter_by(is_archived=True)
        else:
            query = query.filter_by(is_archived=False)

    if query_text:
        like = f"%{query_text}%"
        query = query.filter(
            (Note.title.ilike(like)) | (Note.description.ilike(like))
        )

    if category_id:
        query = query.filter_by(category_id=category_id)

    if tag_id:
        query = query.filter(Note.tags.any(Tag.id == tag_id))

    # Pinned notes first, then most recently updated
    notes = query.order_by(Note.is_pinned.desc(), Note.updated_at.desc()).all()

    categories = Category.query.filter_by(user_id=user_id).all()
    tags = Tag.query.filter_by(user_id=user_id).all()

    return render_template(
        "dashboard.html",
        notes=notes,
        categories=categories,
        tags=tags,
        view=view,
        query_text=query_text,
    )


@notes_bp.route("/add_note", methods=["GET", "POST"])
def add_note():
    if "user_id" not in session:
        flash("You must be logged in to view this page", "warning")
        return redirect(url_for("auth.login"))

    user_id = session["user_id"]
    categories = Category.query.filter_by(user_id=user_id).all()

    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        category_id = request.form.get("category_id") or None
        tag_input = request.form.get("tags", "")  # comma-separated string

        note = Note(
            title=title,
            description=description,
            user_id=user_id,
            category_id=category_id,
        )
        note.tags = _get_or_create_tags(tag_input.split(","), user_id)

        db.session.add(note)
        db.session.commit()

        flash("Note added successfully", "success")
        return redirect(url_for("notes.dashboard"))

    return render_template("add_note.html", categories=categories)


@notes_bp.route("/edit_note/<int:note_id>", methods=["GET", "POST"])
def edit_note(note_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    note = Note.query.get_or_404(note_id)

    if note.user_id != session["user_id"]:
        flash("You cannot edit this note", "danger")
        return redirect(url_for("notes.dashboard"))

    user_id = session["user_id"]
    categories = Category.query.filter_by(user_id=user_id).all()

    if request.method == "POST":
        note.title = request.form["title"]
        note.description = request.form["description"]
        note.category_id = request.form.get("category_id") or None

        tag_input = request.form.get("tags", "")
        note.tags = _get_or_create_tags(tag_input.split(","), user_id)

        db.session.commit()

        flash("Note updated successfully", "success")
        return redirect(url_for("notes.dashboard"))

    existing_tags = ", ".join(tag.name for tag in note.tags)
    return render_template(
        "edit_note.html", note=note, categories=categories, existing_tags=existing_tags
    )


@notes_bp.route("/delete_note/<int:note_id>")
def delete_note(note_id):
    """Soft-delete: moves the note to Trash instead of removing it."""
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    from datetime import datetime, timezone

    note = Note.query.get_or_404(note_id)

    if note.user_id != session["user_id"]:
        flash("You cannot delete this note", "danger")
        return redirect(url_for("notes.dashboard"))

    note.is_deleted = True
    note.deleted_at = datetime.now(timezone.utc)
    db.session.commit()

    flash("Note moved to trash", "info")
    return redirect(url_for("notes.dashboard"))


@notes_bp.route("/restore_note/<int:note_id>")
def restore_note(note_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    note = Note.query.get_or_404(note_id)

    if note.user_id != session["user_id"]:
        flash("You cannot restore this note", "danger")
        return redirect(url_for("notes.dashboard"))

    note.is_deleted = False
    note.deleted_at = None
    db.session.commit()

    flash("Note restored", "success")
    return redirect(url_for("notes.dashboard", view="trash"))


@notes_bp.route("/permanent_delete/<int:note_id>")
def permanent_delete(note_id):
    """Actually removes a note from the database — only allowed from Trash."""
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    note = Note.query.get_or_404(note_id)

    if note.user_id != session["user_id"]:
        flash("You cannot delete this note", "danger")
        return redirect(url_for("notes.dashboard"))

    if not note.is_deleted:
        flash("Move the note to trash before deleting permanently", "warning")
        return redirect(url_for("notes.dashboard"))

    db.session.delete(note)
    db.session.commit()

    flash("Note permanently deleted", "danger")
    return redirect(url_for("notes.dashboard", view="trash"))


@notes_bp.route("/toggle_pin/<int:note_id>")
def toggle_pin(note_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    note = Note.query.get_or_404(note_id)

    if note.user_id != session["user_id"]:
        flash("You cannot modify this note", "danger")
        return redirect(url_for("notes.dashboard"))

    note.is_pinned = not note.is_pinned
    db.session.commit()

    return redirect(url_for("notes.dashboard"))


@notes_bp.route("/toggle_archive/<int:note_id>")
def toggle_archive(note_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    note = Note.query.get_or_404(note_id)

    if note.user_id != session["user_id"]:
        flash("You cannot modify this note", "danger")
        return redirect(url_for("notes.dashboard"))

    note.is_archived = not note.is_archived
    if note.is_archived:
        note.is_pinned = False  # archived notes shouldn't stay pinned to the top
    db.session.commit()

    flash(
        "Note archived" if note.is_archived else "Note unarchived",
        "info",
    )
    return redirect(url_for("notes.dashboard"))