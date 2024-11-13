from typing import Optional, BinaryIO, Literal, List
from pydantic import BaseModel, Field
from datetime import datetime
from pathlib import Path
from decimal import Decimal
from enum import Enum
from typing import Optional
from pydantic import BaseModel
import requests


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


from urllib.parse import quote


class Asset(BaseModel):
    id: int
    note_id: Optional[int]
    location: str
    description: Optional[str]
    created_at: datetime

    def get_markdown_link(self) -> str:
        el = self.get_encoded_location()
        desc = self.get_stripped_location()
        return f"![{desc}](/m/{el})"

    def get_stripped_location(self) -> str:
        return self.location.replace("uploads/", "")

    def get_encoded_location(self) -> str:

        return quote(self.get_stripped_location())


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


class API:
    def __init__(self, base_url: str):
        self.base_url = base_url


class NoteAPI(API):
    def __init__(self, base_url: str):
        super().__init__(base_url)

    def update_notes_tree(self, notes: list[TreeNote]) -> None:
        """
        Update the entire notes tree structure

        Args:
            notes: List of TreeNote objects representing the new tree structure
            base_url: The base URL of the API

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = requests.put(
            f"{self.base_url}/notes/tree",
            headers={"Content-Type": "application/json"},
            json=[note.model_dump(exclude_unset=True) for note in notes],
        )

        response.raise_for_status()

    def note_create(self, title: str, content: str) -> dict:
        """
        Create a new note using the API

        Args:
            title: The title of the note
            content: The content of the note

        Returns:
            dict: The created note data

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        request_data = CreateNoteRequest(title=title, content=content)

        response = requests.post(
            f"{self.base_url}/notes/flat",
            headers={"Content-Type": "application/json"},
            data=request_data.model_dump_json(),
        )

        response.raise_for_status()
        return response.json()

    def get_note(self, note_id: int) -> Note:
        """
        Retrieve a note by its ID

        Args:
            note_id: The ID of the note to retrieve

        Returns:
            Note: The retrieved note data

        Raises:
            requests.exceptions.RequestException: If the request fails
            requests.exceptions.HTTPError: If the note is not found (404)
        """
        response = requests.get(
            f"{self.base_url}/notes/flat/{note_id}",
            headers={"Content-Type": "application/json"},
        )

        response.raise_for_status()
        return Note.model_validate(response.json())

    def get_note_without_content(
        self,
        note_id: int,
    ) -> NoteWithoutContent:
        """
        Retrieve a note by its ID, excluding the content field

        Args:
            note_id: The ID of the note to retrieve

        Returns:
            NoteWithoutContent: The retrieved note data without content

        Raises:
            requests.exceptions.RequestException: If the request fails
            requests.exceptions.HTTPError: If the note is not found (404)
        """
        response = requests.get(
            f"{self.base_url}/notes/flat/{note_id}",
            params={"exclude_content": "true"},
            headers={"Content-Type": "application/json"},
        )

        response.raise_for_status()
        return NoteWithoutContent.model_validate(response.json())

    def get_all_notes(self) -> list[Note]:
        """
        Retrieve all notes

        Args:

        Returns:
            list[Note]: List of all notes

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = requests.get(
            f"{self.base_url}/notes/flat",
            headers={"Content-Type": "application/json"},
        )

        response.raise_for_status()
        return [Note.model_validate(note) for note in response.json()]

    def get_all_notes_without_content(
        self,
    ) -> list[NoteWithoutContent]:
        """
        Retrieve all notes without their content

        Args:

        Returns:
            list[NoteWithoutContent]: List of all notes without content

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = requests.get(
            f"{self.base_url}/notes/flat",
            params={"exclude_content": "true"},
            headers={"Content-Type": "application/json"},
        )

        response.raise_for_status()
        return [NoteWithoutContent.model_validate(note) for note in response.json()]

    def attach_note_to_parent(
        self,
        child_note_id: int,
        parent_note_id: int,
        hierarchy_type: str = "block",
    ) -> None:
        """
        Attach a note as a child of another note

        Args:
            child_note_id: ID of the note to attach as child
            parent_note_id: ID of the parent note
            hierarchy_type: Type of hierarchy relationship (default: "block")

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        request_data = AttachNoteRequest(
            child_note_id=child_note_id,
            parent_note_id=parent_note_id,
            hierarchy_type=hierarchy_type,
        )

        response = requests.post(
            f"{self.base_url}/notes/hierarchy/attach",
            headers={"Content-Type": "application/json"},
            data=request_data.model_dump_json(),
        )

        response.raise_for_status()

    def get_note_hierarchy_relations(
        self,
    ) -> list[NoteHierarchyRelation]:
        """
        Get all parent-child relationships between notes

        Args:

        Returns:
            list[NoteHierarchyRelation]: List of all parent-child relationships

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = requests.get(
            f"{self.base_url}/notes/hierarchy",
            headers={"Content-Type": "application/json"},
        )

        response.raise_for_status()
        return [NoteHierarchyRelation.model_validate(rel) for rel in response.json()]

    def detach_note_from_parent(self, note_id: int) -> None:
        """
        Detach a note from its parent

        Args:
            note_id: ID of the note to detach from its parent

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = requests.delete(
            f"{self.base_url}/notes/hierarchy/detach/{note_id}",
            headers={"Content-Type": "application/json"},
        )

        response.raise_for_status()

    def search_notes(self, query: str) -> list[Note]:
        """
        Search notes using full-text search

        Args:
            query: The search query string

        Returns:
            list[Note]: List of notes matching the search query

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = requests.get(
            f"{self.base_url}/notes/search/fts",
            params={"q": query},
            headers={"Content-Type": "application/json"},
        )

        response.raise_for_status()
        return [Note.model_validate(note) for note in response.json()]

    def update_note(self, note_id: int, request: UpdateNoteRequest) -> Note:
        """
        Update an existing note

        Args:
            note_id: The ID of the note to update
            request: The update request containing new note data

        Returns:
            Note: The updated note data

        Raises:
            requests.exceptions.RequestException: If the request fails
            requests.exceptions.HTTPError: If the note is not found (404)
        """
        response = requests.put(
            f"{self.base_url}/notes/flat/{note_id}",
            headers={"Content-Type": "application/json"},
            data=request.model_dump_json(),
        )

        response.raise_for_status()
        return Note.model_validate(response.json())

    def delete_note(self, note_id: int) -> DeleteNoteResponse:
        """
        Delete a note by its ID

        Args:
            note_id: The ID of the note to delete

        Returns:
            DeleteNoteResponse: Response containing success message and deleted ID

        Raises:
            requests.exceptions.RequestException: If the request fails
            requests.exceptions.HTTPError: If the note is not found (404)
        """
        response = requests.delete(
            f"{self.base_url}/notes/flat/{note_id}",
            headers={"Content-Type": "application/json"},
        )

        response.raise_for_status()
        return DeleteNoteResponse.model_validate(response.json())

    def batch_update_notes(
        self, request: BatchUpdateNotesRequest
    ) -> BatchUpdateNotesResponse:
        """
        Update multiple notes in a single request

        Args:
            request: The batch update request containing note IDs and their updates

        Returns:
            BatchUpdateNotesResponse: Contains lists of successfully updated notes and failed note IDs

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        # Transform the updates list into the API's expected format
        payload = {
            "updates": [
                [id, update.model_dump(exclude_none=True)]
                for id, update in request.updates
            ]
        }

        response = requests.put(
            f"{self.base_url}/notes/flat/batch",
            headers={"Content-Type": "application/json"},
            json=payload,
        )

        response.raise_for_status()
        return BatchUpdateNotesResponse.model_validate(response.json())

    def get_note_backlinks(
        self,
        note_id: int,
    ) -> list[Note]:
        """Get all notes that link to the specified note

        Args:
            note_id: The ID of the note to get backlinks for

        Returns:
            list[Note]: List of notes that link to the specified note

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = requests.get(
            f"{self.base_url}/notes/flat/{note_id}/backlinks",
            headers={"Content-Type": "application/json"},
        )

        response.raise_for_status()
        return [Note.model_validate(note) for note in response.json()]

    def get_note_forward_links(self, note_id: int) -> list[Note]:
        """Get all notes that the specified note links to

        Args:
            note_id: The ID of the note to get forward links for

        Returns:
            list[Note]: List of notes that are linked to by the specified note

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = requests.get(
            f"{self.base_url}/notes/flat/{note_id}/forward-links",
            headers={"Content-Type": "application/json"},
        )

        response.raise_for_status()
        return [Note.model_validate(note) for note in response.json()]

    def get_link_edge_list(self) -> List[LinkEdge]:
        """Get all link edges between notes

        Returns:
            List[LinkEdge]: List of all link edges between notes

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = requests.get(
            f"{self.base_url}/notes/flat/link-edge-list",
            headers={"Content-Type": "application/json"},
        )

        response.raise_for_status()
        return [LinkEdge.model_validate(edge) for edge in response.json()]

    def get_rendered_notes(
        self, format: Literal["md", "html"] = "md"
    ) -> list[RenderedNote]:
        """Get all notes with their content rendered as markdown or HTML

        Args:
            format: The format to render notes in, either "md" or "html" (default: "md")

        Returns:
            list[RenderedNote]: List of notes with rendered content

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = requests.get(
            f"{self.base_url}/notes/flat/render/{format}",
            headers={"Content-Type": "application/json"},
        )

        response.raise_for_status()
        return [RenderedNote.model_validate(note) for note in response.json()]

    def get_rendered_note(
        self,
        note_id: int,
        format: Literal["md", "html"] = "md",
    ) -> str:
        """Get a single note with its content rendered as markdown

        Args:
            note_id: ID of the note to render

        Returns:
            str: The rendered markdown content

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = requests.get(
            f"{self.base_url}/notes/flat/{note_id}/render/{format}",
            headers={"Content-Type": "application/json"},
        )

        response.raise_for_status()
        return response.text

    def render_markdown(
        self,
        content: str,
        format: Optional[Literal["text", "html", "pdf"]] = None,
    ) -> str:
        """Render markdown content to the specified format

        Args:
            content: The markdown content to render
            format: Optional output format (text, html, or pdf)

        Returns:
            str: The rendered content

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        request = RenderMarkdownRequest(content=content, format=format)

        response = requests.post(
            f"{self.base_url}/render/markdown",
            headers={"Content-Type": "application/json"},
            data=request.model_dump_json(exclude_none=True),
        )

        response.raise_for_status()
        return response.text

    def get_notes_tree(self) -> list[TreeNote]:
        """
        Retrieve all notes in a tree structure

        Args:

        Returns:
            list[TreeNote]: List of all notes with their hierarchical structure

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = requests.get(
            f"{self.base_url}/notes/tree",
            headers={"Content-Type": "application/json"},
        )

        response.raise_for_status()
        return [TreeNote.model_validate(note) for note in response.json()]


class TagAPI(API):
    def __init__(self, base_url: str):
        super().__init__(base_url)

    def get_tag(self, tag_id: int) -> Tag:
        """
        Get a tag by its ID

        Args:
            tag_id: The ID of the tag to retrieve

        Returns:
            Tag: The retrieved tag data

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = requests.get(
            f"{self.base_url}/tags/{tag_id}",
            headers={"Content-Type": "application/json"},
        )

        response.raise_for_status()
        return Tag.model_validate(response.json())

    def get_all_tags(self) -> list[Tag]:
        """
        Get all tags

        Args:

        Returns:
            list[Tag]: List of all tags

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = requests.get(
            f"{self.base_url}/tags",
            headers={"Content-Type": "application/json"},
        )

        response.raise_for_status()
        return [Tag.model_validate(tag) for tag in response.json()]

    def update_tag(self, tag_id: int, name: str) -> Tag:
        """
        Update an existing tag

        Args:
            tag_id: The ID of the tag to update
            name: The new name for the tag

        Returns:
            Tag: The updated tag data

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        request_data = CreateTagRequest(name=name)

        response = requests.put(
            f"{self.base_url}/tags/{tag_id}",
            headers={"Content-Type": "application/json"},
            data=request_data.model_dump_json(),
        )

        response.raise_for_status()
        return Tag.model_validate(response.json())

    def delete_tag(self, tag_id: int) -> None:
        """
        Delete a tag by its ID

        Args:
            tag_id: The ID of the tag to delete

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = requests.delete(
            f"{self.base_url}/tags/{tag_id}",
            headers={"Content-Type": "application/json"},
        )

        response.raise_for_status()

    def attach_tag_to_note(
        self,
        note_id: int,
        tag_id: int,
    ) -> None:
        """
        Attach a tag to a note

        Args:
            note_id: The ID of the note
            tag_id: The ID of the tag to attach

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        request_data = AttachTagRequest(note_id=note_id, tag_id=tag_id)

        response = requests.post(
            f"{self.base_url}/tags/notes",
            headers={"Content-Type": "application/json"},
            data=request_data.model_dump_json(),
        )

        response.raise_for_status()

    def detach_tag_from_note(
        self,
        note_id: int,
        tag_id: int,
    ) -> None:
        """
        Detach a tag from a note

        Args:
            note_id: The ID of the note
            tag_id: The ID of the tag to detach

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = requests.delete(
            f"{self.base_url}/tags/notes/{note_id}/{tag_id}",
            headers={"Content-Type": "application/json"},
        )

        response.raise_for_status()

    def get_note_tag_relations(
        self,
    ) -> list[NoteTagRelation]:
        """
        Get all relationships between notes and tags

        Returns:
            list[NoteTagRelation]: List of all note-tag relationships

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = requests.get(
            f"{self.base_url}/tags/notes",
            headers={"Content-Type": "application/json"},
        )

        response.raise_for_status()
        return [NoteTagRelation.model_validate(rel) for rel in response.json()]

    def get_tag_hierarchy_relations(self) -> list[TagHierarchyRelation]:
        """
        Get all parent-child relationships between tags

        Returns:
            list[TagHierarchyRelation]: List of all parent-child relationships between tags

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = requests.get(
            f"{self.base_url}/tags/hierarchy",
            headers={"Content-Type": "application/json"},
        )

        response.raise_for_status()
        return [TagHierarchyRelation.model_validate(rel) for rel in response.json()]

    def attach_tag_to_parent(
        self,
        child_id: int,
        parent_id: int,
    ) -> None:
        """
        Attach a tag as a child of another tag

        Args:
            child_id: ID of the tag to attach as child
            parent_id: ID of the parent tag

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        request_data = AttachTagHierarchyRequest(child_id=child_id, parent_id=parent_id)

        response = requests.post(
            f"{self.base_url}/tags/hierarchy/attach",
            headers={"Content-Type": "application/json"},
            data=request_data.model_dump_json(),
        )

        response.raise_for_status()

    def detach_tag_from_parent(self, tag_id: int) -> None:
        """
        Detach a tag from its parent

        Args:
            tag_id: ID of the tag to detach from its parent

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = requests.delete(
            f"{self.base_url}/tags/hierarchy/detach/{tag_id}",
            headers={"Content-Type": "application/json"},
        )

        response.raise_for_status()

    def create_tag(self, name: str) -> Tag:
        """
        Create a new tag

        Args:
            name: The name of the tag

        Returns:
            Tag: The created tag data

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        request_data = CreateTagRequest(name=name)

        response = requests.post(
            f"{self.base_url}/tags",
            headers={"Content-Type": "application/json"},
            data=request_data.model_dump_json(),
        )

        response.raise_for_status()
        return Tag.model_validate(response.json())

    def get_tags_tree(self) -> list[TreeTagWithNotes]:
        """
        Get all tags in a tree structure

        Returns:
            list[TreeTagWithNotes]: List of all tags with their hierarchical structure

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = requests.get(
            f"{self.base_url}/tags/tree",
            headers={"Content-Type": "application/json"},
        )

        response.raise_for_status()
        return [TreeTagWithNotes.model_validate(tag) for tag in response.json()]


class TaskAPI(API):
    def __init__(self, base_url: str):
        super().__init__(base_url)

    def get_task(self, task_id: int) -> Task:
        """
        Get a task by its ID

        Args:
            task_id: The ID of the task to retrieve

        Returns:
            Task: The retrieved task data

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = requests.get(
            f"{self.base_url}/tasks/{task_id}",
            headers={"Content-Type": "application/json"},
        )

        response.raise_for_status()
        return Task.model_validate(response.json())

    def get_all_tasks(self) -> list[Task]:
        """
        Get all tasks

        Returns:
            list[Task]: List of all tasks

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = requests.get(
            f"{self.base_url}/tasks",
            headers={"Content-Type": "application/json"},
        )

        response.raise_for_status()
        return [Task.model_validate(task) for task in response.json()]

    def get_task_hierarchy_relations(self) -> list[TaskHierarchyRelation]:
        """
        Get all parent-child relationships between tasks

        Returns:
            list[TaskHierarchyRelation]: List of all parent-child relationships between tasks

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = requests.get(
            f"{self.base_url}/tasks/hierarchy",
            headers={"Content-Type": "application/json"},
        )

        response.raise_for_status()
        return [TaskHierarchyRelation.model_validate(rel) for rel in response.json()]

    def update_task(self, task_id: int, task: UpdateTaskRequest) -> Task:
        """
        Update an existing task

        Args:
            task_id: The ID of the task to update
            task: The task data to update

        Returns:
            Task: The updated task data

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = requests.put(
            f"{self.base_url}/tasks/{task_id}",
            headers={"Content-Type": "application/json"},
            data=task.model_dump_json(exclude_none=True),
        )

        response.raise_for_status()
        return Task.model_validate(response.json())

    def delete_task(self, task_id: int) -> None:
        """
        Delete a task by its ID

        Args:
            task_id: The ID of the task to delete

        Raises:
            requests.exceptions.RequestException: If the request fails
            requests.exceptions.HTTPError: If the task is not found (404)
        """
        response = requests.delete(
            f"{self.base_url}/tasks/{task_id}",
            headers={"Content-Type": "application/json"},
        )

        response.raise_for_status()

    def create_task(self, task: CreateTaskRequest) -> Task:
        """
        Create a new task

        Args:
            task: The task data to create

        Returns:
            Task: The created task data

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = requests.post(
            f"{self.base_url}/tasks",
            headers={"Content-Type": "application/json"},
            data=task.model_dump_json(exclude_none=True),
        )

        response.raise_for_status()
        return Task.model_validate(response.json())

    def attach_task_to_parent(self, child_id: int, parent_id: int) -> None:
        """
        Attach a task as a child of another task

        Args:
            child_id: ID of the task to attach as child
            parent_id: ID of the parent task

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        request_data = AttachTaskRequest(
            child_task_id=child_id, parent_task_id=parent_id
        )

        response = requests.post(
            f"{self.base_url}/tasks/hierarchy/attach",
            headers={"Content-Type": "application/json"},
            data=request_data.model_dump_json(),
        )

        response.raise_for_status()

    def detach_task_from_parent(self, task_id: int) -> None:
        """
        Detach a task from its parent

        Args:
            task_id: ID of the task to detach from its parent

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = requests.delete(
            f"{self.base_url}/tasks/hierarchy/detach/{task_id}",
            headers={"Content-Type": "application/json"},
        )

        response.raise_for_status()

    def get_tasks_tree(self) -> list[TreeTask]:
        """
        Get all tasks in a tree structure

        Returns:
            list[TreeTask]: List of all tasks with their hierarchical structure

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = requests.get(
            f"{self.base_url}/tasks/tree",
            headers={"Content-Type": "application/json"},
        )

        response.raise_for_status()
        return [TreeTask.model_validate(task) for task in response.json()]


class AssetAPI(API):
    def __init__(self, base_url: str):
        super().__init__(base_url)

    def upload_asset(self, file_path: str | Path | BinaryIO) -> Asset:
        """
        Upload a file as an asset

        Args:
            file_path: Path to the file to upload or file-like object

        Returns:
            Asset: The created asset data

        Raises:
            requests.exceptions.RequestException: If the request fails
            FileNotFoundError: If the file path does not exist
        """
        if isinstance(file_path, (str, Path)):
            with open(file_path, "rb") as f:
                files = {"file": f}
                response = requests.post(f"{self.base_url}/assets", files=files)
        else:
            # Handle file-like object
            files = {"file": file_path}
            response = requests.post(f"{self.base_url}/assets", files=files)

        response.raise_for_status()
        return Asset.model_validate(response.json())

    def get_all_assets(self) -> list[Asset]:
        """
        Get all assets

        Returns:
            list[Asset]: List of all assets

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = requests.get(
            f"{self.base_url}/assets",
            headers={"Content-Type": "application/json"},
        )

        response.raise_for_status()
        return [Asset.model_validate(asset) for asset in response.json()]

    def update_asset(self, asset_id: int, request: UpdateAssetRequest) -> Asset:
        """
        Update an asset's metadata

        Args:
            asset_id: The ID of the asset to update
            request: The update request containing new metadata

        Returns:
            Asset: The updated asset data

        Raises:
            requests.exceptions.RequestException: If the request fails
            requests.exceptions.HTTPError: If the asset is not found (404)
        """
        response = requests.put(
            f"{self.base_url}/assets/{asset_id}",
            headers={"Content-Type": "application/json"},
            data=request.model_dump_json(exclude_none=True),
        )

        response.raise_for_status()
        return Asset.model_validate(response.json())

    def delete_asset(self, asset_id: int) -> None:
        """
        Delete an asset by its ID

        Args:
            asset_id: The ID of the asset to delete

        Raises:
            requests.exceptions.RequestException: If the request fails
            requests.exceptions.HTTPError: If the asset is not found (404)
        """
        response = requests.delete(
            f"{self.base_url}/assets/{asset_id}",
            headers={"Content-Type": "application/json"},
        )

        response.raise_for_status()

    def download_asset(
        self,
        asset_id: int | str,
        output_path: str | Path,
    ) -> None:
        """
        Download an asset by its ID or filename to a specified path

        Args:
            asset_id: The ID of the asset to download or its filename (e.g. 'icon.png')
            output_path: Path where the downloaded file should be saved

        Raises:
            requests.exceptions.RequestException: If the request fails
            requests.exceptions.HTTPError: If the asset is not found (404)
        """
        endpoint = (
            f"{self.base_url}/assets/download/{asset_id}"
            if isinstance(asset_id, str)
            else f"{self.base_url}/assets/{asset_id}"
        )
        response = requests.get(endpoint, stream=True)
        response.raise_for_status()

        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
