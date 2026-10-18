from dataclasses import asdict, dataclass


@dataclass
class Announcement:
    id: int
    title: str
    content: str
    date: str
    images: list[dict]
    attachments: list[dict]

    @classmethod
    def from_payload(cls, payload: dict) -> "Announcement":
        return cls(
            id=payload.get("id", 0),
            title=payload.get("title", ""),
            content=payload.get("content", ""),
            date=payload.get("date", ""),
            images=payload.get("images") or [],
            attachments=payload.get("attachments") or [],
        )

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Event:
    id: int
    title: str
    summary: str
    description: str
    start_date: str
    end_date: str
    images: list[dict]
    attachments: list[dict]
    links: list[dict]

    @classmethod
    def from_payload(cls, payload: dict) -> "Event":
        return cls(
            id=payload.get("id", 0),
            title=payload.get("title", ""),
            summary=payload.get("summary", ""),
            description=payload.get("description", ""),
            start_date=payload.get("startDate", ""),
            end_date=payload.get("endDate", ""),
            images=payload.get("images") or [],
            attachments=payload.get("attachments") or [],
            links=payload.get("links") or [],
        )

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Document:
    id: int
    title: str
    description: str
    category: str
    publish_date: str
    unit: str
    author: str
    created_at: str
    files: list[dict]

    @classmethod
    def from_payload(cls, payload: dict) -> "Document":
        return cls(
            id=payload.get("id", 0),
            title=payload.get("title", ""),
            description=payload.get("description", ""),
            category=payload.get("category", ""),
            publish_date=payload.get("publishDate", ""),
            unit=payload.get("creationUnit", ""),
            author=payload.get("createdBy", ""),
            created_at=payload.get("createdAt", ""),
            files=payload.get("files") or [],
        )

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class LogKey:
    fingerprint: str
    pubkey: str
    algorithm: str
    purpose: str
    valid_from: str | None
    valid_until: str | None
    revoked: bool
    succession_predecessor: str | None
    succession_log_index: int | None

    @classmethod
    def from_payload(cls, payload: dict) -> "LogKey":
        return cls(
            fingerprint=payload.get("fingerprint", ""),
            pubkey=payload.get("pubkey", ""),
            algorithm=payload.get("algorithm", ""),
            purpose=payload.get("purpose", ""),
            valid_from=payload.get("valid_from"),
            valid_until=payload.get("valid_until"),
            revoked=payload.get("revoked", False),
            succession_predecessor=payload.get("succession_predecessor"),
            succession_log_index=payload.get("succession_log_index"),
        )

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class LogStatus:
    tree_size: int
    root_hash: str
    submissions_total: int
    submissions_this_week: int
    week_start: str
    week_timezone: str
    week_starts_on: str
    pending_total: int
    last_entry_at: str

    @classmethod
    def from_payload(cls, payload: dict) -> "LogStatus":
        return cls(
            tree_size=payload.get("tree_size", 0),
            root_hash=payload.get("root_hash", ""),
            submissions_total=payload.get("submissions_total", 0),
            submissions_this_week=payload.get("submissions_this_week", 0),
            week_start=payload.get("week_start", ""),
            week_timezone=payload.get("week_timezone", ""),
            week_starts_on=payload.get("week_starts_on", ""),
            pending_total=payload.get("pending_total", 0),
            last_entry_at=payload.get("last_entry_at", ""),
        )

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ProofStep:
    position: str
    hash: str

    @classmethod
    def from_payload(cls, payload: dict) -> "ProofStep":
        return cls(
            position=payload.get("position", ""),
            hash=payload.get("hash", ""),
        )

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class InclusionProof:
    idx: int
    tree_size: int
    leaf_hash: str
    root_hash: str
    proof: list[ProofStep]

    @classmethod
    def from_payload(cls, payload: dict) -> "InclusionProof":
        return cls(
            idx=payload.get("idx", 0),
            tree_size=payload.get("tree_size", 0),
            leaf_hash=payload.get("leaf_hash", ""),
            root_hash=payload.get("root_hash", ""),
            proof=[ProofStep.from_payload(step) for step in payload.get("proof") or []],
        )

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class LeafData:
    """日誌葉節點內容。

    submission 條目帶 ``server_timestamp``，decision 條目帶 ``timestamp``，
    所以兩者都是選填欄位。
    """

    type: str
    commit_digest: str
    signature: str
    signing_key_fp: str
    timestamp: str | None = None
    server_timestamp: str | None = None
    decision_type: str | None = None
    decision_text_hash: str | None = None
    reply_text_hash: str | None = None

    @classmethod
    def from_payload(cls, payload: dict) -> "LeafData":
        return cls(
            type=payload.get("type", ""),
            commit_digest=payload.get("commit_digest", ""),
            signature=payload.get("signature", ""),
            signing_key_fp=payload.get("signing_key_fp", ""),
            timestamp=payload.get("timestamp"),
            server_timestamp=payload.get("server_timestamp"),
            decision_type=payload.get("decision_type"),
            decision_text_hash=payload.get("decision_text_hash"),
            reply_text_hash=payload.get("reply_text_hash"),
        )

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class LogEntry:
    idx: int
    leaf_hash: str
    entry_type: str
    timestamp: str
    leaf_data: LeafData | None = None

    @classmethod
    def from_payload(cls, payload: dict) -> "LogEntry":
        leaf_data = payload.get("leaf_data")
        return cls(
            idx=payload.get("idx", 0),
            leaf_hash=payload.get("leaf_hash", ""),
            entry_type=payload.get("entry_type", ""),
            timestamp=payload.get("timestamp", ""),
            leaf_data=LeafData.from_payload(leaf_data) if isinstance(leaf_data, dict) else None,
        )

    def to_dict(self) -> dict:
        return asdict(self)

