from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    func,
)
from sqlalchemy.orm import relationship

from ..db import Base


class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class JobVideo(Base):
    __tablename__ = "job_videos"

    id = Column(Integer, primary_key=True, index=True)
    uploader_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    trade_id = Column(Integer, ForeignKey("trades.id"), nullable=False)

    file_url = Column(Text, nullable=False)
    thumbnail_url = Column(Text, nullable=True)
    original_filename = Column(String(255), nullable=True)
    duration_sec = Column(Integer, nullable=True)

    status = Column(String(50), nullable=False, default="uploaded")
    # 'uploaded', 'processing', 'processed', 'failed'

    job_type_free_text = Column(Text, nullable=True)
    location_type = Column(String(50), nullable=True)  # 'kitchen', 'bathroom', etc.
    difficulty_level = Column(Integer, nullable=True)  # 1–5

    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    uploader = relationship("User", backref="job_videos")
    trade = relationship("Trade", backref="job_videos")
    lesson = relationship("Lesson", back_populates="job_video", uselist=False)


class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    job_video_id = Column(Integer, ForeignKey("job_videos.id"), nullable=False)
    trade_id = Column(Integer, ForeignKey("trades.id"), nullable=False)

    title = Column(String(255), nullable=False)
    short_description = Column(Text, nullable=True)
    language_main = Column(String(10), nullable=False, default="en")

    status = Column(String(50), nullable=False, default="draft")
    # 'draft', 'ready', 'published', 'hidden'

    estimated_duration_min = Column(Integer, nullable=True)
    thumbnail_url = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    job_video = relationship("JobVideo", back_populates="lesson")
    trade = relationship("Trade", backref="lessons")
    steps = relationship("LessonStep", back_populates="lesson", cascade="all, delete-orphan")
    transcripts = relationship("LessonTranscript", back_populates="lesson", cascade="all, delete-orphan")

    tags = relationship(
        "Tag",
        secondary="lesson_tags",
        back_populates="lessons",
    )


class LessonStep(Base):
    __tablename__ = "lesson_steps"

    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)

    step_number = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    start_time_sec = Column(Integer, nullable=False)
    end_time_sec = Column(Integer, nullable=True)

    ai_confidence = Column(Integer, nullable=True)  # optional, 0–100 or leave null

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    lesson = relationship("Lesson", back_populates="steps")
    tools = relationship(
        "Tool",
        secondary="lesson_step_tools",
        back_populates="steps",
    )
    materials = relationship(
        "Material",
        secondary="lesson_step_materials",
        back_populates="steps",
    )


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=True)  # 'fixture_type', 'task_type', etc.
    trade_id = Column(Integer, ForeignKey("trades.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    trade = relationship("Trade", backref="tags")
    lessons = relationship(
        "Lesson",
        secondary="lesson_tags",
        back_populates="tags",
    )


class LessonTag(Base):
    __tablename__ = "lesson_tags"

    lesson_id = Column(Integer, ForeignKey("lessons.id"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id"), primary_key=True)


class Tool(Base):
    __tablename__ = "tools"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    trade_id = Column(Integer, ForeignKey("trades.id"), nullable=True)
    aliases = Column(Text, nullable=True)  # you can store JSON later

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    trade = relationship("Trade", backref="tools")
    steps = relationship(
        "LessonStep",
        secondary="lesson_step_tools",
        back_populates="tools",
    )


class Material(Base):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    trade_id = Column(Integer, ForeignKey("trades.id"), nullable=True)
    aliases = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    trade = relationship("Trade", backref="materials")
    steps = relationship(
        "LessonStep",
        secondary="lesson_step_materials",
        back_populates="materials",
    )


class LessonStepTool(Base):
    __tablename__ = "lesson_step_tools"

    lesson_step_id = Column(Integer, ForeignKey("lesson_steps.id"), primary_key=True)
    tool_id = Column(Integer, ForeignKey("tools.id"), primary_key=True)


class LessonStepMaterial(Base):
    __tablename__ = "lesson_step_materials"

    lesson_step_id = Column(Integer, ForeignKey("lesson_steps.id"), primary_key=True)
    material_id = Column(Integer, ForeignKey("materials.id"), primary_key=True)


class LessonTranscript(Base):
    __tablename__ = "lesson_transcripts"

    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)

    raw_transcript = Column(Text, nullable=True)
    script_narration = Column(Text, nullable=True)
    subtitles_srt = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    lesson = relationship("Lesson", back_populates="transcripts")
