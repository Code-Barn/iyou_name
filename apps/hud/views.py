"""
Chart generation bridge view connecting Django to the compiled iyou_chart_kernel
Rust/PyO3 extension for high-performance rendering.
"""

import json
import logging
from collections import deque

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404

from apps.generator.models import GedcomFile
from apps.parser.models import PersonData

logger = logging.getLogger(__name__)

try:
    import iyou_chart_kernel
except ImportError:
    iyou_chart_kernel = None


def _build_ancestor_matrix(individuals, root_id, depth):
    """
    Walk up the tree from root_id for *depth* generations and return
    a JSON-serialisable list-of-dicts describing each ancestor at each level.
    """
    queue = deque([(root_id, 0)])
    matrix = []
    visited = set()

    while queue:
        person_id, gen = queue.popleft()
        if person_id in visited or gen >= depth:
            continue
        visited.add(person_id)

        raw = individuals.get(person_id)
        if raw is None:
            continue

        person = (
            raw
            if isinstance(raw, PersonData)
            else PersonData(**raw) if isinstance(raw, dict) else None
        )
        if person is None:
            continue

        entry = person.to_dict()
        entry["generation"] = gen
        matrix.append(entry)

        if person.father:
            queue.append((person.father, gen + 1))
        if person.mother:
            queue.append((person.mother, gen + 1))

    return matrix


@login_required
def generate_tree_chart(request, document_id):
    """
    Render a tree chart PNG by piping profile data through the compiled
    Rust iyou_chart_kernel FFI extension.  Falls back to 503 when the
    native module has not been compiled / installed yet.
    """
    if iyou_chart_kernel is None:
        return HttpResponse(
            "Native compilation engine offline.", status=503
        )

    try:
        doc = GedcomFile.objects.get(id=document_id, user=request.user)
    except GedcomFile.DoesNotExist:
        raise Http404("Target dataset missing.")

    if not doc.parsed_data:
        return HttpResponse("File not processed yet.", status=400)

    individuals = doc.parsed_data.get("individuals", {})
    root_id = doc.home_person_id or request.session.get("selected_individual_id")

    if not root_id or root_id not in individuals:
        return HttpResponse("No valid root individual.", status=400)

    raw_root = individuals[root_id]
    primary_person = (
        raw_root
        if isinstance(raw_root, PersonData)
        else PersonData(**raw_root) if isinstance(raw_root, dict) else None
    )
    if primary_person is None:
        return HttpResponse("Malformed root individual data.", status=400)

    generation_depth = int(request.GET.get("depth", 7))

    settings_payload = json.dumps({"theme": "dark", "layout": "radial"})
    primary_payload = json.dumps(primary_person.to_dict())
    ancestors_payload = json.dumps(
        _build_ancestor_matrix(individuals, root_id, generation_depth)
    )

    try:
        chart_bytes = iyou_chart_kernel.render_chart_from_json(
            generation_depth,
            primary_payload,
            ancestors_payload,
            settings_payload,
        )
    except Exception as e:
        logger.error("Rendering pipeline failure: %s", e)
        return HttpResponse(
            f"Rendering pipeline failure: {e}", status=500
        )

    response = HttpResponse(chart_bytes, content_type="image/png")
    response["Content-Disposition"] = (
        f'inline; filename="chart_{document_id}.png"'
    )
    return response
