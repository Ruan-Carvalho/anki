# Copyright: Ankitects Pty Ltd and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import os
import tempfile
import pytest

from anki.collection import CardStats
from tests.shared import getEmptyCol
from anki.stats import StreakTracker

def test_stats():
    col = getEmptyCol()
    note = col.newNote()
    note["Front"] = "foo"
    col.addNote(note)
    c = note.cards()[0]
    # card stats
    card_stats = col.card_stats_data(c.id)
    assert card_stats.note_id == note.id
    c = col.sched.getCard()
    col.sched.answerCard(c, 3)
    col.sched.answerCard(c, 2)
    card_stats = col.card_stats_data(c.id)
    assert len(card_stats.revlog) == 2


def test_graphs_empty():
    col = getEmptyCol()
    assert col.stats().report()


def test_graphs():
    dir = tempfile.gettempdir()
    col = getEmptyCol()
    g = col.stats()
    rep = g.report()
    with open(os.path.join(dir, "test.html"), "w", encoding="UTF-8") as note:
        note.write(rep)
    return

def test_average_over_last_7_days():
    history = [50, 100, 150, 80, 90, 120, 110]  # total = 700, média = 100
    tracker = StreakTracker(daily_goal=100, history=history)
    assert tracker.average() == 100

def test_is_on_track_when_meeting_goal():
    history = [100, 100, 100, 100, 100, 100, 100]
    tracker = StreakTracker(daily_goal=100, history=history)
    assert tracker.is_on_track()

def test_is_not_on_track_when_below_goal():
    history = [30, 40, 20, 50, 35, 45, 60]
    tracker = StreakTracker(daily_goal=80, history=history)
    assert not tracker.is_on_track()

def test_progress_percentage():
    history = [80, 90, 100, 110, 120, 130, 140]  # média: 110
    tracker = StreakTracker(daily_goal=100, history=history)
    assert tracker.progress_percentage() == 100

def test_progress_percentage_capped_at_100():
    history = [300, 400, 500]  # média: 400
    tracker = StreakTracker(daily_goal=100, history=history)
    assert tracker.progress_percentage() == 100

def test_empty_history_returns_zero_average():
    tracker = StreakTracker(daily_goal=100, history=[])
    assert tracker.average() == 0
    assert not tracker.is_on_track()
    assert tracker.progress_percentage() == 0
