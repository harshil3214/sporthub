from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Literal

import requests
from django.core.management.base import BaseCommand, CommandError
from django.utils.dateparse import parse_datetime

from core.models import FootballMatch, Team, VolleyballMatch
from core.services import API_SPORTS_KEY, sync_football, sync_volleyball


SportKey = Literal["football", "volleyball"]


@dataclass(frozen=True)
class LiveFixture:
    external_api_id: str
    home_name: str
    away_name: str
    kickoff_iso: str | None


def _fetch_api_sports_live_fixtures(sport: SportKey) -> list[LiveFixture]:
    host = f"v1.{sport}.api-sports.io"
    if sport == "football":
        host = "v3.football.api-sports.io"

    url = f"https://{host}/fixtures?live=all"
    headers = {"x-apisports-key": API_SPORTS_KEY, "x-apisports-host": host}

    resp = requests.get(url, headers=headers, timeout=15)
    data = resp.json()

    fixtures: list[LiveFixture] = []
    for item in data.get("response", []) or []:
        fixture = item.get("fixture") or {}
        teams = item.get("teams") or {}
        home = (teams.get("home") or {}).get("name") or "Home"
        away = (teams.get("away") or {}).get("name") or "Away"
        fixture_id = fixture.get("id")
        if fixture_id is None:
            continue
        fixtures.append(
            LiveFixture(
                external_api_id=str(fixture_id),
                home_name=str(home)[:100],
                away_name=str(away)[:100],
                kickoff_iso=fixture.get("date"),
            )
        )
    return fixtures


def _get_or_create_team(name: str, sport_code: str) -> Team:
    # Keep a stable unique-ish key by (name, sport). No unique constraint in DB,
    # so we use get_or_create best-effort.
    team, _ = Team.objects.get_or_create(name=name, sport=sport_code)
    return team


class Command(BaseCommand):
    help = "Fetch live fixtures (API-Sports) and create/update matches in your DB."

    def add_arguments(self, parser):
        parser.add_argument(
            "--sport",
            required=True,
            choices=["football", "volleyball"],
            help="Which sport live fixtures to fetch from API-Sports.",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=15,
            help="Maximum number of live fixtures to import/update.",
        )

    def handle(self, *args, **options):
        sport: SportKey = options["sport"]
        limit: int = options["limit"]
        if limit <= 0:
            raise CommandError("--limit must be > 0")

        fixtures = _fetch_api_sports_live_fixtures(sport)[:limit]
        if not fixtures:
            self.stdout.write(self.style.WARNING("No live fixtures found right now. Try again later."))
            return

        created = 0
        updated = 0

        for fx in fixtures:
            if sport == "football":
                match_model = FootballMatch
                sync_fn = sync_football
                sport_code = "FOOTBALL"
            else:
                match_model = VolleyballMatch
                sync_fn = sync_volleyball
                sport_code = "VOLLEYBALL"

            home_team = _get_or_create_team(fx.home_name, sport_code)
            away_team = _get_or_create_team(fx.away_name, sport_code)

            match, was_created = match_model.objects.get_or_create(
                external_api_id=fx.external_api_id,
                defaults={
                    "home_team": home_team,
                    "away_team": away_team,
                    "data_source": "API",
                    "status": "LIVE",
                },
            )

            # If teams were wrong / blank, align them to the live fixture.
            # (Keeps your dashboard meaningful.)
            changed = False
            if match.home_team_id != home_team.id:
                match.home_team = home_team
                changed = True
            if match.away_team_id != away_team.id:
                match.away_team = away_team
                changed = True

            if fx.kickoff_iso:
                dt = parse_datetime(fx.kickoff_iso)
                if dt and match.match_datetime != dt:
                    match.match_datetime = dt
                    changed = True

            if match.data_source != "API":
                match.data_source = "API"
                changed = True
            if match.status != "LIVE":
                match.status = "LIVE"
                changed = True

            if changed:
                match.save()

            ok = sync_fn(match)
            if was_created:
                created += 1
            else:
                updated += 1

            if not ok:
                self.stdout.write(self.style.WARNING(f"Failed syncing fixture {fx.external_api_id} ({fx.home_name} vs {fx.away_name})."))

        self.stdout.write(self.style.SUCCESS(f"Done. Created {created}, updated {updated}."))
