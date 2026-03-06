from sqlalchemy import Column, Float, Integer, Boolean, Date, DateTime, String, Text, ForeignKey, UUID
from sqlalchemy.orm import mapped_column, Mapped, relationship
from datetime import datetime, timezone
from uuid import uuid4, UUID as UUIDV4
from .base import Base


class GoverningBody(Base):
    """Reference table for sanctioning / governing bodies (USFSA, ISI, etc.)."""

    __tablename__ = 'e_governing_bodies'
    __table_args__ = {'extend_existing': True}

    id: Mapped[UUIDV4] = mapped_column(primary_key=True, default=uuid4)
    short_name = Column(String, nullable=False)
    full_name = Column(String)

    event_types = relationship("EventType", back_populates="governing_body_rel")

    def __init__(self, short_name, full_name=None, id=None):
        if id is not None:
            self.id = id
        self.short_name = short_name
        self.full_name = full_name

    def __repr__(self):
        return f"<GoverningBody({self.short_name})>"


class EventType(Base):
    """Dimensional table combining category, scoring system, and governing body.

    Replaces the old e_competition_types table.  The UI derives display
    labels from category + scoring_system + governing body short_name.
    """

    __tablename__ = 'e_event_types'
    __table_args__ = {'extend_existing': True}

    id: Mapped[UUIDV4] = mapped_column(primary_key=True, default=uuid4)
    category = Column(String, nullable=False)
    scoring_system = Column(String, nullable=True)
    governing_body_id = Column(UUID, ForeignKey("e_governing_bodies.id"), nullable=True)
    single_mark = Column(Boolean, default=False)

    governing_body_rel = relationship("GoverningBody", back_populates="event_types")

    def __init__(self, category, scoring_system=None, governing_body_id=None,
                 single_mark=False, id=None):
        if id is not None:
            self.id = id
        self.category = category
        self.scoring_system = scoring_system
        self.governing_body_id = governing_body_id
        self.single_mark = single_mark

    def __repr__(self):
        return f"<EventType({self.category}/{self.scoring_system})>"


COST_CATEGORIES = [
    "Competition Entry",
    "Practice Ice",
    "Admin Fee",
    "Coach Fee",
    "Taxes",
    "Other",
]


class SkaterEvent(Base):
    """Parent record for a competition, showcase, or exhibition.

    One SkaterEvent contains one or more EventEntry children (individual
    segments the skater performed at the event).
    """

    __tablename__ = 'e_events'
    __table_args__ = {'extend_existing': True}

    id: Mapped[UUIDV4] = mapped_column(primary_key=True, default=uuid4)

    event_label = Column(String, nullable=False)
    event_date = Column(Date, nullable=False)
    event_location = Column(UUID, ForeignKey("locations.rink_id", ondelete='SET NULL'),
                            nullable=True)
    hosting_club = Column(UUID, ForeignKey("club_directory.club_id", ondelete='SET NULL'),
                          nullable=True)
    coach_id = Column(UUID, ForeignKey("coaches.coach_id", ondelete='SET NULL'),
                      nullable=True)
    notes = Column(Text, nullable=True)

    uSkaterUUID = Column(UUID, ForeignKey("uSkaterConfig.uSkaterUUID", ondelete='CASCADE'),
                         nullable=False)
    uSkaterConfig = Column(UUID, ForeignKey("uSkateConfig.sConfigID", ondelete='SET NULL'),
                           nullable=True)

    entries = relationship("EventEntry", back_populates="event",
                           cascade="all, delete-orphan", passive_deletes=True)
    costs = relationship("EventCost", back_populates="event",
                         cascade="all, delete-orphan", passive_deletes=True)

    @property
    def event_cost(self):
        """Derived total: sum of (amount * quantity) across all cost line items."""
        if not self.costs:
            return 0.0
        return sum(c.amount * c.quantity for c in self.costs)

    def __init__(self, event_label, event_date, uSkaterUUID,
                 event_location=None, hosting_club=None, coach_id=None,
                 notes=None, uSkaterConfig=None):
        self.event_label = event_label
        self.event_date = event_date
        self.event_location = event_location
        self.hosting_club = hosting_club
        self.coach_id = coach_id
        self.notes = notes
        self.uSkaterUUID = uSkaterUUID
        self.uSkaterConfig = uSkaterConfig

    def __repr__(self):
        return f"<SkaterEvent({self.event_label}, {self.event_date})>"


class EventCost(Base):
    """Individual cost line item for an event (entry fee, practice ice, etc.)."""

    __tablename__ = 'e_event_costs'
    __table_args__ = {'extend_existing': True}

    id: Mapped[UUIDV4] = mapped_column(primary_key=True, default=uuid4)

    event_id = Column(UUID, ForeignKey("e_events.id", ondelete='CASCADE'), nullable=False)
    category = Column(String, nullable=False)
    note = Column(String, nullable=True)
    amount = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False, default=1)

    event = relationship("SkaterEvent", back_populates="costs")

    def __init__(self, event_id, category, amount, quantity=1, note=None):
        self.event_id = event_id
        self.category = category
        self.amount = amount
        self.quantity = quantity
        self.note = note

    def __repr__(self):
        return f"<EventCost({self.category}, ${self.amount} x{self.quantity})>"


class EventEntry(Base):
    """One segment / program a skater performed at an event."""

    __tablename__ = 'e_event_entries'
    __table_args__ = {'extend_existing': True}

    id: Mapped[UUIDV4] = mapped_column(primary_key=True, default=uuid4)

    event_id = Column(UUID, ForeignKey("e_events.id", ondelete='CASCADE'), nullable=False)
    entry_date = Column(Date, nullable=True)
    event_segment = Column(String, nullable=True)
    event_level = Column(String, nullable=True)
    event_type = Column(UUID, ForeignKey("e_event_types.id"), nullable=True)

    placement = Column(Integer, nullable=True)
    field_size = Column(Integer, nullable=True)
    majority = Column(String, nullable=True)
    total_segment_score = Column(Float, nullable=True)

    status = Column(String, nullable=False, default="Committed")

    source_url = Column(String, nullable=True)
    video_url = Column(String, nullable=True)
    event_results = Column(String, nullable=True)

    uSkaterUUID = Column(UUID, ForeignKey("uSkaterConfig.uSkaterUUID", ondelete='CASCADE'),
                         nullable=False)

    event = relationship("SkaterEvent", back_populates="entries")
    scores_6_0 = relationship("Score6_0", back_populates="entry",
                              cascade="all, delete-orphan", passive_deletes=True)
    scores_cjs = relationship("ScoreCJS", back_populates="entry",
                              cascade="all, delete-orphan", passive_deletes=True)
    scores_ijs_components = relationship("ScoreIJSComponent", back_populates="entry",
                                        cascade="all, delete-orphan", passive_deletes=True)
    scores_ijs_elements = relationship("ScoreIJSElement", back_populates="entry",
                                      cascade="all, delete-orphan", passive_deletes=True)
    deductions = relationship("EventDeduction", back_populates="entry",
                              cascade="all, delete-orphan", passive_deletes=True)
    event_type_rel = relationship("EventType", foreign_keys=[event_type])

    def __init__(self, event_id, uSkaterUUID, event_segment=None, event_level=None,
                 event_type=None, placement=None, field_size=None, majority=None,
                 total_segment_score=None, source_url=None, video_url=None,
                 event_results=None, status="Committed"):
        self.event_id = event_id
        self.event_segment = event_segment
        self.event_level = event_level
        self.event_type = event_type
        self.placement = placement
        self.field_size = field_size
        self.majority = majority
        self.total_segment_score = total_segment_score
        self.source_url = source_url
        self.video_url = video_url
        self.event_results = event_results
        self.status = status
        self.uSkaterUUID = uSkaterUUID

    def __repr__(self):
        return f"<EventEntry({self.event_segment}, level={self.event_level}, place={self.placement})>"


class Score6_0(Base):
    """Per-judge scores for the 6.0 (ordinal) scoring system.

    One row per judge per entry.  technical_merit and presentation are
    the two marks; ordinal is the judge's placement ranking.
    """

    __tablename__ = 'e_scores_6_0'
    __table_args__ = {'extend_existing': True}

    id: Mapped[UUIDV4] = mapped_column(primary_key=True, default=uuid4)

    entry_id = Column(UUID, ForeignKey("e_event_entries.id", ondelete='CASCADE'), nullable=False)
    judge_number = Column(Integer, nullable=False)
    ordinal = Column(Float, nullable=True)
    technical_merit = Column(Float, nullable=True)
    presentation = Column(Float, nullable=True)

    uSkaterUUID = Column(UUID, ForeignKey("uSkaterConfig.uSkaterUUID", ondelete='CASCADE'),
                         nullable=False)

    entry = relationship("EventEntry", back_populates="scores_6_0")

    def __init__(self, entry_id, judge_number, uSkaterUUID, ordinal=None,
                 technical_merit=None, presentation=None):
        self.entry_id = entry_id
        self.judge_number = judge_number
        self.ordinal = ordinal
        self.technical_merit = technical_merit
        self.presentation = presentation
        self.uSkaterUUID = uSkaterUUID

    def __repr__(self):
        return f"<Score6_0(judge={self.judge_number}, tm={self.technical_merit}, pres={self.presentation})>"


class ScoreCJS(Base):
    """Per-judge scores for the CJS (Component Judging System).

    One row per judge per entry.  CJS uses three component marks:
    artistic_appeal, performance, and skating_skills (each 0.25-10.0).
    """

    __tablename__ = 'e_scores_cjs'
    __table_args__ = {'extend_existing': True}

    id: Mapped[UUIDV4] = mapped_column(primary_key=True, default=uuid4)

    entry_id = Column(UUID, ForeignKey("e_event_entries.id", ondelete='CASCADE'), nullable=False)
    judge_number = Column(Integer, nullable=False)
    artistic_appeal = Column(Float, nullable=True)
    performance = Column(Float, nullable=True)
    skating_skills = Column(Float, nullable=True)

    uSkaterUUID = Column(UUID, ForeignKey("uSkaterConfig.uSkaterUUID", ondelete='CASCADE'),
                         nullable=False)

    entry = relationship("EventEntry", back_populates="scores_cjs")

    def __init__(self, entry_id, judge_number, uSkaterUUID, artistic_appeal=None,
                 performance=None, skating_skills=None):
        self.entry_id = entry_id
        self.judge_number = judge_number
        self.artistic_appeal = artistic_appeal
        self.performance = performance
        self.skating_skills = skating_skills
        self.uSkaterUUID = uSkaterUUID

    def __repr__(self):
        return f"<ScoreCJS(judge={self.judge_number}, art={self.artistic_appeal}, perf={self.performance}, sk={self.skating_skills})>"


class ScoreIJSComponent(Base):
    """Per-judge program component scores for IJS.

    One row per judge per entry.  IJS uses three component marks:
    composition, presentation, and skating_skills (each 0.25-10.0).
    """

    __tablename__ = 'e_scores_ijs_components'
    __table_args__ = {'extend_existing': True}

    id: Mapped[UUIDV4] = mapped_column(primary_key=True, default=uuid4)

    entry_id = Column(UUID, ForeignKey("e_event_entries.id", ondelete='CASCADE'), nullable=False)
    judge_number = Column(Integer, nullable=False)
    composition = Column(Float, nullable=True)
    presentation = Column(Float, nullable=True)
    skating_skills = Column(Float, nullable=True)

    uSkaterUUID = Column(UUID, ForeignKey("uSkaterConfig.uSkaterUUID", ondelete='CASCADE'),
                         nullable=False)

    entry = relationship("EventEntry", back_populates="scores_ijs_components")

    def __init__(self, entry_id, judge_number, uSkaterUUID, composition=None,
                 presentation=None, skating_skills=None):
        self.entry_id = entry_id
        self.judge_number = judge_number
        self.composition = composition
        self.presentation = presentation
        self.skating_skills = skating_skills
        self.uSkaterUUID = uSkaterUUID

    def __repr__(self):
        return f"<ScoreIJSComponent(judge={self.judge_number}, comp={self.composition}, pres={self.presentation}, sk={self.skating_skills})>"


class ScoreIJSElement(Base):
    """Per-element technical scores for IJS.

    One row per element performed in the program.  Each element has a
    base_value determined by its level, plus a GOE (grade of execution,
    -5 to +5) awarded by the panel.
    """

    __tablename__ = 'e_scores_ijs_elements'
    __table_args__ = {'extend_existing': True}

    id: Mapped[UUIDV4] = mapped_column(primary_key=True, default=uuid4)

    entry_id = Column(UUID, ForeignKey("e_event_entries.id", ondelete='CASCADE'), nullable=False)
    element_number = Column(Integer, nullable=False)
    element_name = Column(String, nullable=True)
    base_value = Column(Float, nullable=True)
    goe = Column(Float, nullable=True)
    final_score = Column(Float, nullable=True)

    uSkaterUUID = Column(UUID, ForeignKey("uSkaterConfig.uSkaterUUID", ondelete='CASCADE'),
                         nullable=False)

    entry = relationship("EventEntry", back_populates="scores_ijs_elements")

    def __init__(self, entry_id, element_number, uSkaterUUID, element_name=None,
                 base_value=None, goe=None, final_score=None):
        self.entry_id = entry_id
        self.element_number = element_number
        self.element_name = element_name
        self.base_value = base_value
        self.goe = goe
        self.final_score = final_score
        self.uSkaterUUID = uSkaterUUID

    def __repr__(self):
        return f"<ScoreIJSElement(#{self.element_number} {self.element_name}, bv={self.base_value}, goe={self.goe})>"


class EventDeduction(Base):
    """Deductions applied to an entry (falls, time violations, etc.)."""

    __tablename__ = 'e_deductions'
    __table_args__ = {'extend_existing': True}

    id: Mapped[UUIDV4] = mapped_column(primary_key=True, default=uuid4)

    entry_id = Column(UUID, ForeignKey("e_event_entries.id", ondelete='CASCADE'), nullable=False)
    deduction_type = Column(String, nullable=False)
    value = Column(Float, nullable=False, default=0.0)
    notes = Column(Text, nullable=True)

    uSkaterUUID = Column(UUID, ForeignKey("uSkaterConfig.uSkaterUUID", ondelete='CASCADE'),
                         nullable=False)

    entry = relationship("EventEntry", back_populates="deductions")

    def __init__(self, entry_id, deduction_type, value, uSkaterUUID, notes=None):
        self.entry_id = entry_id
        self.deduction_type = deduction_type
        self.value = value
        self.notes = notes
        self.uSkaterUUID = uSkaterUUID

    def __repr__(self):
        return f"<EventDeduction({self.deduction_type}, -{self.value})>"


class ImportLog(Base):
    """Audit log for URL-based results imports."""

    __tablename__ = 'e_import_log'
    __table_args__ = {'extend_existing': True}

    id: Mapped[UUIDV4] = mapped_column(primary_key=True, default=uuid4)

    source_url = Column(String, nullable=False)
    source_type = Column(String, nullable=False, default="usfsa_6.0")
    status = Column(String, nullable=False)
    skater_name_searched = Column(String, nullable=False)
    skater_name_matched = Column(String, nullable=True)

    event_id = Column(UUID, ForeignKey("e_events.id", ondelete="SET NULL"), nullable=True)
    entry_id = Column(UUID, ForeignKey("e_event_entries.id", ondelete="SET NULL"), nullable=True)

    raw_html = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False)

    uSkaterUUID = Column(UUID, ForeignKey("uSkaterConfig.uSkaterUUID", ondelete='CASCADE'),
                         nullable=False)

    def __init__(self, source_url, status, skater_name_searched, uSkaterUUID,
                 source_type="usfsa_6.0", skater_name_matched=None,
                 event_id=None, entry_id=None, raw_html=None,
                 error_message=None, created_at=None):
        self.source_url = source_url
        self.source_type = source_type
        self.status = status
        self.skater_name_searched = skater_name_searched
        self.skater_name_matched = skater_name_matched
        self.event_id = event_id
        self.entry_id = entry_id
        self.raw_html = raw_html
        self.error_message = error_message
        self.created_at = created_at or datetime.now(timezone.utc)
        self.uSkaterUUID = uSkaterUUID

    def __repr__(self):
        return f"<ImportLog({self.source_url}, status={self.status})>"
