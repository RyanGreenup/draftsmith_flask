from typing import Optional, BinaryIO, Literal, List, Union
from pydantic import BaseModel, Field
from datetime import datetime, date
from pathlib import Path
from decimal import Decimal
from enum import Enum
from typing import Optional
from pydantic import BaseModel
import requests
import json
import tempfile
import os


class Note(BaseModel):
    id: int
    title: str
    content: str
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None


class CreateNoteRequest(BaseModel):
    title: str
    content: str


class UpdateNoteRequest(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None


class BatchUpdateNotesRequest(BaseModel):
    updates: list[tuple[int, UpdateNoteRequest]]


class BatchUpdateNotesResponse(BaseModel):
    updated: list[Note]
    failed: list[int]


class DeleteNoteResponse(BaseModel):
    message: str
    deleted_id: int


class LinkEdge(BaseModel):
    """Represents a link between two notes"""

    from_: int = Field(alias="from")  # from is a Python keyword
    to: int


class NoteWithoutContent(BaseModel):
    id: int
    title: str
    created_at: datetime
    modified_at: datetime


class AttachNoteRequest(BaseModel):
    child_note_id: int
    parent_note_id: int
    hierarchy_type: str


class NoteHierarchyRelation(BaseModel):
    parent_id: int
    child_id: int


class Tag(BaseModel):
    id: int
    name: str


class CreateTagRequest(BaseModel):
    name: str


class AttachTagRequest(BaseModel):
    note_id: int
    tag_id: int


class NoteTagRelation(BaseModel):
    note_id: int
    tag_id: int


class TagHierarchyRelation(BaseModel):
    parent_id: int
    child_id: int


class AttachTagHierarchyRequest(BaseModel):
    parent_id: int
    child_id: int


class TreeTag(BaseModel):
    id: int
    name: str


class TreeNote(BaseModel):
    id: int
    title: str
    content: Optional[str] = None
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None
    hierarchy_type: Optional[str] = None
    children: list["TreeNote"] = []
    tags: list[TreeTag] = []


class UpdateAssetRequest(BaseModel):
    note_id: Optional[int] = None
    description: Optional[str] = None


class Asset(BaseModel):
    id: int
    note_id: Optional[int]
    location: str
    description: Optional[str]
    created_at: datetime


class RenderedNote(BaseModel):
    """Represents a note with rendered markdown content"""

    id: int
    rendered_content: str


class RenderMarkdownRequest(BaseModel):
    """Request to render markdown content"""

    content: str
    format: Optional[Literal["text", "html", "pdf"]] = None


class TreeTagWithNotes(BaseModel):
    id: int
    name: str
    children: list["TreeTagWithNotes"] = []
    notes: list["TreeNote"] = []


def update_notes_tree(
    notes: list[TreeNote], base_url: str = "http://localhost:37240"
) -> None:
    """
    Update the entire notes tree structure

    Args:
        notes: List of TreeNote objects representing the new tree structure
        base_url: The base URL of the API (default: http://localhost:37240)

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    response = requests.put(
        f"{base_url}/notes/tree",
        headers={"Content-Type": "application/json"},
        json=[note.model_dump(exclude_unset=True) for note in notes],
    )

    response.raise_for_status()


def note_create(
    title: str, content: str, base_url: str = "http://localhost:37240"
) -> dict:
    """
    Create a new note using the API

    Args:
        title: The title of the note
        content: The content of the note
        base_url: The base URL of the API (default: http://localhost:37240)

    Returns:
        dict: The created note data

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    request_data = CreateNoteRequest(title=title, content=content)

    response = requests.post(
        f"{base_url}/notes/flat",
        headers={"Content-Type": "application/json"},
        data=request_data.model_dump_json(),
    )

    response.raise_for_status()
    return response.json()


def get_note(note_id: int, base_url: str = "http://localhost:37240") -> Note:
    """
    Retrieve a note by its ID

    Args:
        note_id: The ID of the note to retrieve
        base_url: The base URL of the API (default: http://localhost:37240)

    Returns:
        Note: The retrieved note data

    Raises:
        requests.exceptions.RequestException: If the request fails
        requests.exceptions.HTTPError: If the note is not found (404)
    """
    response = requests.get(
        f"{base_url}/notes/flat/{note_id}",
        headers={"Content-Type": "application/json"},
    )

    response.raise_for_status()
    return Note.model_validate(response.json())


def get_note_without_content(
    note_id: int, base_url: str = "http://localhost:37240"
) -> NoteWithoutContent:
    """
    Retrieve a note by its ID, excluding the content field

    Args:
        note_id: The ID of the note to retrieve
        base_url: The base URL of the API (default: http://localhost:37240)

    Returns:
        NoteWithoutContent: The retrieved note data without content

    Raises:
        requests.exceptions.RequestException: If the request fails
        requests.exceptions.HTTPError: If the note is not found (404)
    """
    response = requests.get(
        f"{base_url}/notes/flat/{note_id}",
        params={"exclude_content": "true"},
        headers={"Content-Type": "application/json"},
    )

    response.raise_for_status()
    return NoteWithoutContent.model_validate(response.json())


def get_all_notes(base_url: str = "http://localhost:37240") -> list[Note]:
    """
    Retrieve all notes

    Args:
        base_url: The base URL of the API (default: http://localhost:37240)

    Returns:
        list[Note]: List of all notes

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    response = requests.get(
        f"{base_url}/notes/flat",
        headers={"Content-Type": "application/json"},
    )

    response.raise_for_status()
    return [Note.model_validate(note) for note in response.json()]


def get_all_notes_without_content(
    base_url: str = "http://localhost:37240",
) -> list[NoteWithoutContent]:
    """
    Retrieve all notes without their content

    Args:
        base_url: The base URL of the API (default: http://localhost:37240)

    Returns:
        list[NoteWithoutContent]: List of all notes without content

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    response = requests.get(
        f"{base_url}/notes/flat",
        params={"exclude_content": "true"},
        headers={"Content-Type": "application/json"},
    )

    response.raise_for_status()
    return [NoteWithoutContent.model_validate(note) for note in response.json()]


def attach_note_to_parent(
    child_note_id: int,
    parent_note_id: int,
    hierarchy_type: str = "block",
    base_url: str = "http://localhost:37240",
) -> None:
    """
    Attach a note as a child of another note

    Args:
        child_note_id: ID of the note to attach as child
        parent_note_id: ID of the parent note
        hierarchy_type: Type of hierarchy relationship (default: "block")
        base_url: The base URL of the API (default: http://localhost:37240)

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    request_data = AttachNoteRequest(
        child_note_id=child_note_id,
        parent_note_id=parent_note_id,
        hierarchy_type=hierarchy_type,
    )

    response = requests.post(
        f"{base_url}/notes/hierarchy/attach",
        headers={"Content-Type": "application/json"},
        data=request_data.model_dump_json(),
    )

    response.raise_for_status()


def get_note_hierarchy_relations(
    base_url: str = "http://localhost:37240",
) -> list[NoteHierarchyRelation]:
    """
    Get all parent-child relationships between notes

    Args:
        base_url: The base URL of the API (default: http://localhost:37240)

    Returns:
        list[NoteHierarchyRelation]: List of all parent-child relationships

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    response = requests.get(
        f"{base_url}/notes/hierarchy",
        headers={"Content-Type": "application/json"},
    )

    response.raise_for_status()
    return [NoteHierarchyRelation.model_validate(rel) for rel in response.json()]


def detach_note_from_parent(
    note_id: int, base_url: str = "http://localhost:37240"
) -> None:
    """
    Detach a note from its parent

    Args:
        note_id: ID of the note to detach from its parent
        base_url: The base URL of the API (default: http://localhost:37240)

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    response = requests.delete(
        f"{base_url}/notes/hierarchy/detach/{note_id}",
        headers={"Content-Type": "application/json"},
    )

    response.raise_for_status()


def get_tag(tag_id: int, base_url: str = "http://localhost:37240") -> Tag:
    """
    Get a tag by its ID

    Args:
        tag_id: The ID of the tag to retrieve
        base_url: The base URL of the API (default: http://localhost:37240)

    Returns:
        Tag: The retrieved tag data

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    response = requests.get(
        f"{base_url}/tags/{tag_id}",
        headers={"Content-Type": "application/json"},
    )

    response.raise_for_status()
    return Tag.model_validate(response.json())


def get_all_tags(base_url: str = "http://localhost:37240") -> list[Tag]:
    """
    Get all tags

    Args:
        base_url: The base URL of the API (default: http://localhost:37240)

    Returns:
        list[Tag]: List of all tags

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    response = requests.get(
        f"{base_url}/tags",
        headers={"Content-Type": "application/json"},
    )

    response.raise_for_status()
    return [Tag.model_validate(tag) for tag in response.json()]


def update_tag(tag_id: int, name: str, base_url: str = "http://localhost:37240") -> Tag:
    """
    Update an existing tag

    Args:
        tag_id: The ID of the tag to update
        name: The new name for the tag
        base_url: The base URL of the API (default: http://localhost:37240)

    Returns:
        Tag: The updated tag data

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    request_data = CreateTagRequest(name=name)

    response = requests.put(
        f"{base_url}/tags/{tag_id}",
        headers={"Content-Type": "application/json"},
        data=request_data.model_dump_json(),
    )

    response.raise_for_status()
    return Tag.model_validate(response.json())


def delete_tag(tag_id: int, base_url: str = "http://localhost:37240") -> None:
    """
    Delete a tag by its ID

    Args:
        tag_id: The ID of the tag to delete
        base_url: The base URL of the API (default: http://localhost:37240)

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    response = requests.delete(
        f"{base_url}/tags/{tag_id}",
        headers={"Content-Type": "application/json"},
    )

    response.raise_for_status()


def attach_tag_to_note(
    note_id: int, tag_id: int, base_url: str = "http://localhost:37240"
) -> None:
    """
    Attach a tag to a note

    Args:
        note_id: The ID of the note
        tag_id: The ID of the tag to attach
        base_url: The base URL of the API (default: http://localhost:37240)

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    request_data = AttachTagRequest(note_id=note_id, tag_id=tag_id)

    response = requests.post(
        f"{base_url}/tags/notes",
        headers={"Content-Type": "application/json"},
        data=request_data.model_dump_json(),
    )

    response.raise_for_status()


def detach_tag_from_note(
    note_id: int, tag_id: int, base_url: str = "http://localhost:37240"
) -> None:
    """
    Detach a tag from a note

    Args:
        note_id: The ID of the note
        tag_id: The ID of the tag to detach
        base_url: The base URL of the API (default: http://localhost:37240)

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    response = requests.delete(
        f"{base_url}/tags/notes/{note_id}/{tag_id}",
        headers={"Content-Type": "application/json"},
    )

    response.raise_for_status()


def get_note_tag_relations(
    base_url: str = "http://localhost:37240",
) -> list[NoteTagRelation]:
    """
    Get all relationships between notes and tags

    Args:
        base_url: The base URL of the API (default: http://localhost:37240)

    Returns:
        list[NoteTagRelation]: List of all note-tag relationships

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    response = requests.get(
        f"{base_url}/tags/notes",
        headers={"Content-Type": "application/json"},
    )

    response.raise_for_status()
    return [NoteTagRelation.model_validate(rel) for rel in response.json()]


def get_tag_hierarchy_relations(
    base_url: str = "http://localhost:37240",
) -> list[TagHierarchyRelation]:
    """
    Get all parent-child relationships between tags

    Args:
        base_url: The base URL of the API (default: http://localhost:37240)

    Returns:
        list[TagHierarchyRelation]: List of all parent-child relationships between tags

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    response = requests.get(
        f"{base_url}/tags/hierarchy",
        headers={"Content-Type": "application/json"},
    )

    response.raise_for_status()
    return [TagHierarchyRelation.model_validate(rel) for rel in response.json()]


def attach_tag_to_parent(
    child_id: int, parent_id: int, base_url: str = "http://localhost:37240"
) -> None:
    """
    Attach a tag as a child of another tag

    Args:
        child_id: ID of the tag to attach as child
        parent_id: ID of the parent tag
        base_url: The base URL of the API (default: http://localhost:37240)

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    request_data = AttachTagHierarchyRequest(child_id=child_id, parent_id=parent_id)

    response = requests.post(
        f"{base_url}/tags/hierarchy/attach",
        headers={"Content-Type": "application/json"},
        data=request_data.model_dump_json(),
    )

    response.raise_for_status()


def detach_tag_from_parent(
    tag_id: int, base_url: str = "http://localhost:37240"
) -> None:
    """
    Detach a tag from its parent

    Args:
        tag_id: ID of the tag to detach from its parent
        base_url: The base URL of the API (default: http://localhost:37240)

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    response = requests.delete(
        f"{base_url}/tags/hierarchy/detach/{tag_id}",
        headers={"Content-Type": "application/json"},
    )

    response.raise_for_status()


def create_tag(name: str, base_url: str = "http://localhost:37240") -> Tag:
    """
    Create a new tag

    Args:
        name: The name of the tag
        base_url: The base URL of the API (default: http://localhost:37240)

    Returns:
        Tag: The created tag data

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    request_data = CreateTagRequest(name=name)

    response = requests.post(
        f"{base_url}/tags",
        headers={"Content-Type": "application/json"},
        data=request_data.model_dump_json(),
    )

    response.raise_for_status()
    return Tag.model_validate(response.json())


def get_tags_tree(base_url: str = "http://localhost:37240") -> list[TreeTagWithNotes]:
    """
    Get all tags in a tree structure

    Args:
        base_url: The base URL of the API (default: http://localhost:37240)

    Returns:
        list[TreeTagWithNotes]: List of all tags with their hierarchical structure

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    response = requests.get(
        f"{base_url}/tags/tree",
        headers={"Content-Type": "application/json"},
    )

    response.raise_for_status()
    return [TreeTagWithNotes.model_validate(tag) for tag in response.json()]


class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"


class CreateTaskRequest(BaseModel):
    note_id: Optional[int] = None
    status: TaskStatus = TaskStatus.TODO
    effort_estimate: Optional[Decimal] = None
    actual_effort: Optional[Decimal] = None
    deadline: Optional[datetime] = None
    priority: Optional[int] = None
    all_day: bool = False
    goal_relationship: Optional[str] = None


class UpdateTaskRequest(BaseModel):
    note_id: Optional[int] = None
    status: Optional[TaskStatus] = None
    effort_estimate: Optional[Decimal] = None
    actual_effort: Optional[Decimal] = None
    deadline: Optional[datetime] = None
    priority: Optional[int] = None
    all_day: Optional[bool] = None
    goal_relationship: Optional[str] = None


class AttachTaskRequest(BaseModel):
    child_task_id: int
    parent_task_id: int


class TaskHierarchyRelation(BaseModel):
    parent_id: int
    child_id: int


class TreeTask(BaseModel):
    id: int
    note_id: Optional[int]
    status: TaskStatus
    effort_estimate: Optional[Decimal]
    actual_effort: Optional[Decimal]
    deadline: Optional[datetime]
    priority: Optional[int]
    created_at: datetime
    modified_at: datetime
    all_day: bool
    goal_relationship: Optional[str]
    children: list["TreeTask"] = []


class Task(BaseModel):
    id: int
    note_id: Optional[int]
    status: TaskStatus
    effort_estimate: Optional[Decimal]
    actual_effort: Optional[Decimal]
    deadline: Optional[datetime]
    priority: Optional[int]
    created_at: datetime
    modified_at: datetime
    all_day: bool
    goal_relationship: Optional[str]


def get_task(task_id: int, base_url: str = "http://localhost:37240") -> Task:
    """
    Get a task by its ID

    Args:
        task_id: The ID of the task to retrieve
        base_url: The base URL of the API (default: http://localhost:37240)

    Returns:
        Task: The retrieved task data

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    response = requests.get(
        f"{base_url}/tasks/{task_id}",
        headers={"Content-Type": "application/json"},
    )

    response.raise_for_status()
    return Task.model_validate(response.json())


def get_all_tasks(base_url: str = "http://localhost:37240") -> list[Task]:
    """
    Get all tasks

    Args:
        base_url: The base URL of the API (default: http://localhost:37240)

    Returns:
        list[Task]: List of all tasks

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    response = requests.get(
        f"{base_url}/tasks",
        headers={"Content-Type": "application/json"},
    )

    response.raise_for_status()
    return [Task.model_validate(task) for task in response.json()]


def get_task_hierarchy_relations(
    base_url: str = "http://localhost:37240",
) -> list[TaskHierarchyRelation]:
    """
    Get all parent-child relationships between tasks

    Args:
        base_url: The base URL of the API (default: http://localhost:37240)

    Returns:
        list[TaskHierarchyRelation]: List of all parent-child relationships between tasks

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    response = requests.get(
        f"{base_url}/tasks/hierarchy",
        headers={"Content-Type": "application/json"},
    )

    response.raise_for_status()
    return [TaskHierarchyRelation.model_validate(rel) for rel in response.json()]


def update_task(
    task_id: int, task: UpdateTaskRequest, base_url: str = "http://localhost:37240"
) -> Task:
    """
    Update an existing task

    Args:
        task_id: The ID of the task to update
        task: The task data to update
        base_url: The base URL of the API (default: http://localhost:37240)

    Returns:
        Task: The updated task data

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    response = requests.put(
        f"{base_url}/tasks/{task_id}",
        headers={"Content-Type": "application/json"},
        data=task.model_dump_json(exclude_none=True),
    )

    response.raise_for_status()
    return Task.model_validate(response.json())


def delete_task(task_id: int, base_url: str = "http://localhost:37240") -> None:
    """
    Delete a task by its ID

    Args:
        task_id: The ID of the task to delete
        base_url: The base URL of the API (default: http://localhost:37240)

    Raises:
        requests.exceptions.RequestException: If the request fails
        requests.exceptions.HTTPError: If the task is not found (404)
    """
    response = requests.delete(
        f"{base_url}/tasks/{task_id}",
        headers={"Content-Type": "application/json"},
    )

    response.raise_for_status()


def create_task(
    task: CreateTaskRequest, base_url: str = "http://localhost:37240"
) -> Task:
    """
    Create a new task

    Args:
        task: The task data to create
        base_url: The base URL of the API (default: http://localhost:37240)

    Returns:
        Task: The created task data

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    response = requests.post(
        f"{base_url}/tasks",
        headers={"Content-Type": "application/json"},
        data=task.model_dump_json(exclude_none=True),
    )

    response.raise_for_status()
    return Task.model_validate(response.json())


def attach_task_to_parent(
    child_id: int, parent_id: int, base_url: str = "http://localhost:37240"
) -> None:
    """
    Attach a task as a child of another task

    Args:
        child_id: ID of the task to attach as child
        parent_id: ID of the parent task
        base_url: The base URL of the API (default: http://localhost:37240)

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    request_data = AttachTaskRequest(child_task_id=child_id, parent_task_id=parent_id)

    response = requests.post(
        f"{base_url}/tasks/hierarchy/attach",
        headers={"Content-Type": "application/json"},
        data=request_data.model_dump_json(),
    )

    response.raise_for_status()


def detach_task_from_parent(
    task_id: int, base_url: str = "http://localhost:37240"
) -> None:
    """
    Detach a task from its parent

    Args:
        task_id: ID of the task to detach from its parent
        base_url: The base URL of the API (default: http://localhost:37240)

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    response = requests.delete(
        f"{base_url}/tasks/hierarchy/detach/{task_id}",
        headers={"Content-Type": "application/json"},
    )

    response.raise_for_status()


def get_tasks_tree(base_url: str = "http://localhost:37240") -> list[TreeTask]:
    """
    Get all tasks in a tree structure

    Args:
        base_url: The base URL of the API (default: http://localhost:37240)

    Returns:
        list[TreeTask]: List of all tasks with their hierarchical structure

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    response = requests.get(
        f"{base_url}/tasks/tree",
        headers={"Content-Type": "application/json"},
    )

    response.raise_for_status()
    return [TreeTask.model_validate(task) for task in response.json()]


def upload_asset(
    file_path: str | Path | BinaryIO, base_url: str = "http://localhost:37240"
) -> Asset:
    """
    Upload a file as an asset

    Args:
        file_path: Path to the file to upload or file-like object
        base_url: The base URL of the API (default: http://localhost:37240)

    Returns:
        Asset: The created asset data

    Raises:
        requests.exceptions.RequestException: If the request fails
        FileNotFoundError: If the file path does not exist
    """
    if isinstance(file_path, (str, Path)):
        with open(file_path, "rb") as f:
            files = {"file": f}
            response = requests.post(f"{base_url}/assets", files=files)
    else:
        # Handle file-like object
        files = {"file": file_path}
        response = requests.post(f"{base_url}/assets", files=files)

    response.raise_for_status()
    return Asset.model_validate(response.json())


def get_all_assets(base_url: str = "http://localhost:37240") -> list[Asset]:
    """
    Get all assets

    Args:
        base_url: The base URL of the API (default: http://localhost:37240)

    Returns:
        list[Asset]: List of all assets

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    response = requests.get(
        f"{base_url}/assets",
        headers={"Content-Type": "application/json"},
    )

    response.raise_for_status()
    return [Asset.model_validate(asset) for asset in response.json()]


def update_asset(
    asset_id: int, request: UpdateAssetRequest, base_url: str = "http://localhost:37240"
) -> Asset:
    """
    Update an asset's metadata

    Args:
        asset_id: The ID of the asset to update
        request: The update request containing new metadata
        base_url: The base URL of the API (default: http://localhost:37240)

    Returns:
        Asset: The updated asset data

    Raises:
        requests.exceptions.RequestException: If the request fails
        requests.exceptions.HTTPError: If the asset is not found (404)
    """
    response = requests.put(
        f"{base_url}/assets/{asset_id}",
        headers={"Content-Type": "application/json"},
        data=request.model_dump_json(exclude_none=True),
    )

    response.raise_for_status()
    return Asset.model_validate(response.json())


def delete_asset(asset_id: int, base_url: str = "http://localhost:37240") -> None:
    """
    Delete an asset by its ID

    Args:
        asset_id: The ID of the asset to delete
        base_url: The base URL of the API (default: http://localhost:37240)

    Raises:
        requests.exceptions.RequestException: If the request fails
        requests.exceptions.HTTPError: If the asset is not found (404)
    """
    response = requests.delete(
        f"{base_url}/assets/{asset_id}",
        headers={"Content-Type": "application/json"},
    )

    response.raise_for_status()


def download_asset(
    asset_id: int | str,
    output_path: str | Path,
    base_url: str = "http://localhost:37240",
) -> None:
    """
    Download an asset by its ID or filename to a specified path

    Args:
        asset_id: The ID of the asset to download or its filename (e.g. 'icon.png')
        output_path: Path where the downloaded file should be saved
        base_url: The base URL of the API (default: http://localhost:37240)

    Raises:
        requests.exceptions.RequestException: If the request fails
        requests.exceptions.HTTPError: If the asset is not found (404)
    """
    endpoint = (
        f"{base_url}/assets/download/{asset_id}"
        if isinstance(asset_id, str)
        else f"{base_url}/assets/{asset_id}"
    )
    response = requests.get(endpoint, stream=True)
    response.raise_for_status()

    with open(output_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)


def search_notes(query: str, base_url: str = "http://localhost:37240") -> list[Note]:
    """
    Search notes using full-text search

    Args:
        query: The search query string
        base_url: The base URL of the API (default: http://localhost:37240)

    Returns:
        list[Note]: List of notes matching the search query

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    response = requests.get(
        f"{base_url}/notes/search/fts",
        params={"q": query},
        headers={"Content-Type": "application/json"},
    )

    response.raise_for_status()
    return [Note.model_validate(note) for note in response.json()]


def update_note(
    note_id: int, request: UpdateNoteRequest, base_url: str = "http://localhost:37240"
) -> Note:
    """
    Update an existing note

    Args:
        note_id: The ID of the note to update
        request: The update request containing new note data
        base_url: The base URL of the API (default: http://localhost:37240)

    Returns:
        Note: The updated note data

    Raises:
        requests.exceptions.RequestException: If the request fails
        requests.exceptions.HTTPError: If the note is not found (404)
    """
    response = requests.put(
        f"{base_url}/notes/flat/{note_id}",
        headers={"Content-Type": "application/json"},
        data=request.model_dump_json(),
    )

    response.raise_for_status()
    return Note.model_validate(response.json())


def delete_note(
    note_id: int, base_url: str = "http://localhost:37240"
) -> DeleteNoteResponse:
    """
    Delete a note by its ID

    Args:
        note_id: The ID of the note to delete
        base_url: The base URL of the API (default: http://localhost:37240)

    Returns:
        DeleteNoteResponse: Response containing success message and deleted ID

    Raises:
        requests.exceptions.RequestException: If the request fails
        requests.exceptions.HTTPError: If the note is not found (404)
    """
    response = requests.delete(
        f"{base_url}/notes/flat/{note_id}",
        headers={"Content-Type": "application/json"},
    )

    response.raise_for_status()
    return DeleteNoteResponse.model_validate(response.json())


def batch_update_notes(
    request: BatchUpdateNotesRequest, base_url: str = "http://localhost:37240"
) -> BatchUpdateNotesResponse:
    """
    Update multiple notes in a single request

    Args:
        request: The batch update request containing note IDs and their updates
        base_url: The base URL of the API (default: http://localhost:37240)

    Returns:
        BatchUpdateNotesResponse: Contains lists of successfully updated notes and failed note IDs

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    # Transform the updates list into the API's expected format
    payload = {
        "updates": [
            [id, update.model_dump(exclude_none=True)] for id, update in request.updates
        ]
    }

    response = requests.put(
        f"{base_url}/notes/flat/batch",
        headers={"Content-Type": "application/json"},
        json=payload,
    )

    response.raise_for_status()
    return BatchUpdateNotesResponse.model_validate(response.json())


def get_note_backlinks(
    note_id: int, base_url: str = "http://localhost:37240"
) -> list[Note]:
    """Get all notes that link to the specified note

    Args:
        note_id: The ID of the note to get backlinks for
        base_url: The base URL of the API (default: http://localhost:37240)

    Returns:
        list[Note]: List of notes that link to the specified note

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    response = requests.get(
        f"{base_url}/notes/flat/{note_id}/backlinks",
        headers={"Content-Type": "application/json"},
    )

    response.raise_for_status()
    return [Note.model_validate(note) for note in response.json()]


def get_note_forward_links(
    note_id: int, base_url: str = "http://localhost:37240"
) -> list[Note]:
    """Get all notes that the specified note links to

    Args:
        note_id: The ID of the note to get forward links for
        base_url: The base URL of the API (default: http://localhost:37240)

    Returns:
        list[Note]: List of notes that are linked to by the specified note

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    response = requests.get(
        f"{base_url}/notes/flat/{note_id}/forward-links",
        headers={"Content-Type": "application/json"},
    )

    response.raise_for_status()
    return [Note.model_validate(note) for note in response.json()]


def get_link_edge_list(base_url: str = "http://localhost:37240") -> List[LinkEdge]:
    """Get all link edges between notes

    Args:
        base_url: The base URL of the API (default: http://localhost:37240)

    Returns:
        List[LinkEdge]: List of all link edges between notes

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    response = requests.get(
        f"{base_url}/notes/flat/link-edge-list",
        headers={"Content-Type": "application/json"},
    )

    response.raise_for_status()
    return [LinkEdge.model_validate(edge) for edge in response.json()]


def get_rendered_notes(
    base_url: str = "http://localhost:37240", format: Literal["md", "html"] = "md"
) -> list[RenderedNote]:
    """Get all notes with their content rendered as markdown or HTML

    Args:
        base_url: The base URL of the API (default: http://localhost:37240)
        format: The format to render notes in, either "md" or "html" (default: "md")

    Returns:
        list[RenderedNote]: List of notes with rendered content

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    response = requests.get(
        f"{base_url}/notes/flat/render/{format}",
        headers={"Content-Type": "application/json"},
    )

    response.raise_for_status()
    return [RenderedNote.model_validate(note) for note in response.json()]


def get_rendered_note(
    note_id: int,
    base_url: str = "http://localhost:37240",
    format: Literal["md", "html"] = "md",
) -> str:
    """Get a single note with its content rendered as markdown

    Args:
        note_id: ID of the note to render
        base_url: The base URL of the API (default: http://localhost:37240)

    Returns:
        str: The rendered markdown content

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    response = requests.get(
        f"{base_url}/notes/flat/{note_id}/render/{format}",
        headers={"Content-Type": "application/json"},
    )

    response.raise_for_status()
    return response.text
    """Get all notes with their content rendered as markdown

    Args:
        base_url: The base URL of the API (default: http://localhost:37240)

    Returns:
        list[RenderedNote]: List of notes with rendered markdown content

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    response = requests.get(
        f"{base_url}/notes/flat/render/md",
        headers={"Content-Type": "application/json"},
    )

    response.raise_for_status()
    return [RenderedNote.model_validate(note) for note in response.json()]


def render_markdown(
    content: str,
    format: Optional[Literal["text", "html", "pdf"]] = None,
    base_url: str = "http://localhost:37240",
) -> str:
    """Render markdown content to the specified format

    Args:
        content: The markdown content to render
        format: Optional output format (text, html, or pdf)
        base_url: The base URL of the API (default: http://localhost:37240)

    Returns:
        str: The rendered content

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    request = RenderMarkdownRequest(content=content, format=format)

    response = requests.post(
        f"{base_url}/render/markdown",
        headers={"Content-Type": "application/json"},
        data=request.model_dump_json(exclude_none=True),
    )

    response.raise_for_status()
    return response.text


def render_markdown(
    content: str,
    format: Optional[Literal["text", "html", "pdf"]] = None,
    base_url: str = "http://localhost:37240",
) -> str:
    """Render markdown content to the specified format

    Args:
        content: The markdown content to render
        format: Optional output format (text, html, or pdf)
        base_url: The base URL of the API (default: http://localhost:37240)

    Returns:
        str: The rendered content

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    request = RenderMarkdownRequest(content=content, format=format)

    response = requests.post(
        f"{base_url}/render/markdown",
        headers={"Content-Type": "application/json"},
        data=request.model_dump_json(exclude_none=True),
    )

    response.raise_for_status()
    return response.text


def get_notes_tree(base_url: str = "http://localhost:37240") -> list[TreeNote]:
    """
    Retrieve all notes in a tree structure

    Args:
        base_url: The base URL of the API (default: http://localhost:37240)

    Returns:
        list[TreeNote]: List of all notes with their hierarchical structure

    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    response = requests.get(
        f"{base_url}/notes/tree",
        headers={"Content-Type": "application/json"},
    )

    response.raise_for_status()
    return [TreeNote.model_validate(note) for note in response.json()]
