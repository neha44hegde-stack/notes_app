import os
import re
import uuid
from datetime import datetime, timezone

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    current_app,
    send_from_directory,
    abort,
)
from werkzeug.utils import secure_filename
import bleach

from extensions import db
from models import Note, Tag, Category, Attachment

notes_bp = Blueprint("notes", __name__)

ALLOWED_TAGS = [
    "p", "br", "strong", "em", "u", "s", "ul", "ol", "li",
    "h1", "h2", "h3", "blockquote", "a", "code", "pre", "span"
]
ALLOWED_ATTRS = {
    "a": ["href", "target", "rel"],
    "span": ["class"],
}


def _sanitize_html(raw_html):
    return bleach.clean(
        raw_html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS, strip=True
    )


def _get_or_create_tags(tag_names, user_id):
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
    return tags


def _allowed_file(filename):
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in current_app.config["ALLOWED_EXTENSIONS"]


def _save_attachments(files, note):
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_folder, exist_ok=True)

    for file in files:
        if not file or file.filename == "":
            continue
        if not _allowed_file(file.filename):
            flash(f"File type not allowed: {file.filename}", "warning")
            continue

        original_name = secure_filename(file.filename)
        ext = original_name.rsplit(".", 1)[1].lower()
        stored_name = f"{uuid.uuid4().hex}.{ext}"

        file.save(os.path.join(upload_folder, stored_name))

        attachment = Attachment(
            filename=stored_name,
            original_filename=original_name,
            note_id=note.id,
        )
        db.session.add(attachment)


@notes_bp.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        flash("You must be logged in to view this page", "warning")
        return redirect(url_for("auth.login"))

    user_id = session["user_id"]
    view = request.args.get("view", "active")
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
        description = _sanitize_html(request.form["description"])
        category_id = request.form.get("category_id") or None
        tag_input = request.form.get("tags", "")

        note = Note(
            title=title,
            description=description,
            user_id=user_id,
            category_id=category_id,
        )
        note.tags = _get_or_create_tags(tag_input.split(","), user_id)

        db.session.add(note)
        db.session.flush()

        uploaded_files = request.files.getlist("attachments")
        _save_attachments(uploaded_files, note)

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
        note.description = _sanitize_html(request.form["description"])
        note.category_id = request.form.get("category_id") or None

        tag_input = request.form.get("tags", "")
        note.tags = _get_or_create_tags(tag_input.split(","), user_id)

        uploaded_files = request.files.getlist("attachments")
        _save_attachments(uploaded_files, note)

        db.session.commit()

        flash("Note updated successfully", "success")
        return redirect(url_for("notes.dashboard"))

    existing_tags = ", ".join(tag.name for tag in note.tags)
    return render_template(
        "edit_note.html", note=note, categories=categories, existing_tags=existing_tags
    )


@notes_bp.route("/view_note/<int:note_id>")
def view_note(note_id):
    if "user_id" not in session:
        flash("You must be logged in to view this page", "warning")
        return redirect(url_for("auth.login"))

    note = Note.query.get_or_404(note_id)

    if note.user_id != session["user_id"]:
        flash("You cannot view this note", "danger")
        return redirect(url_for("notes.dashboard"))

    return render_template("view_note.html", note=note)


@notes_bp.route("/summarize_note/<int:note_id>", methods=["POST"])
def summarize_note(note_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    note = Note.query.get_or_404(note_id)

    if note.user_id != session["user_id"]:
        flash("You cannot summarize this note", "danger")
        return redirect(url_for("notes.dashboard"))

    plain_text = re.sub("<[^<]+?>", "", note.description).strip()

    if len(plain_text.split()) < 15:
        flash("Note is too short to summarize meaningfully", "warning")
        return redirect(url_for("notes.view_note", note_id=note.id))

    try:
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

        model_name = "sshleifer/distilbart-cnn-6-6"

        tokenizer = current_app.config.get("SUMMARIZER_TOKENIZER")
        model = current_app.config.get("SUMMARIZER_MODEL")

        if tokenizer is None or model is None:
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
            current_app.config["SUMMARIZER_TOKENIZER"] = tokenizer
            current_app.config["SUMMARIZER_MODEL"] = model

        inputs = tokenizer(
            plain_text, return_tensors="pt", max_length=1024, truncation=True
        )
        summary_ids = model.generate(
            inputs["input_ids"],
            max_length=80,
            min_length=20,
            num_beams=4,
            early_stopping=True,
        )
        summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True).strip()

        note.ai_summary = summary
        db.session.commit()
        flash("Summary generated", "success")
    except Exception as e:
        flash(f"Failed to generate summary: {e}", "danger")

    return redirect(url_for("notes.view_note", note_id=note.id))


@notes_bp.route("/delete_note/<int:note_id>")
def delete_note(note_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

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
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    note = Note.query.get_or_404(note_id)

    if note.user_id != session["user_id"]:
        flash("You cannot delete this note", "danger")
        return redirect(url_for("notes.dashboard"))

    if not note.is_deleted:
        flash("Move the note to trash before deleting permanently", "warning")
        return redirect(url_for("notes.dashboard"))

    upload_folder = current_app.config["UPLOAD_FOLDER"]
    for attachment in note.attachments:
        file_path = os.path.join(upload_folder, attachment.filename)
        if os.path.exists(file_path):
            os.remove(file_path)

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
        note.is_pinned = False
    db.session.commit()

    flash(
        "Note archived" if note.is_archived else "Note unarchived",
        "info",
    )
    return redirect(url_for("notes.dashboard"))


@notes_bp.route("/download_attachment/<int:attachment_id>")
def download_attachment(attachment_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    attachment = Attachment.query.get_or_404(attachment_id)

    if attachment.note.user_id != session["user_id"]:
        abort(403)

    upload_folder = current_app.config["UPLOAD_FOLDER"]
    return send_from_directory(
        upload_folder,
        attachment.filename,
        as_attachment=True,
        download_name=attachment.original_filename,
    )


@notes_bp.route("/delete_attachment/<int:attachment_id>")
def delete_attachment(attachment_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    attachment = Attachment.query.get_or_404(attachment_id)
    note = attachment.note

    if note.user_id != session["user_id"]:
        abort(403)

    upload_folder = current_app.config["UPLOAD_FOLDER"]
    file_path = os.path.join(upload_folder, attachment.filename)
    if os.path.exists(file_path):
        os.remove(file_path)

    db.session.delete(attachment)
    db.session.commit()

    flash("Attachment removed", "info")
    return redirect(url_for("notes.edit_note", note_id=note.id))



